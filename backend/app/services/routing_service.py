"""
Intelligent Routing Service - AI-powered ticket assignment
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketCategory, TicketPriority


class RoutingService:
    """Intelligently route tickets to best available agent"""
    
    async def assign_best_agent(
        self,
        db: Session,
        ticket_id: str,
        ticket: Ticket = None
    ) -> Optional[str]:
        """
        Find and assign the best agent for a ticket
        
        Logic:
        1. Find agents with matching skills
        2. Check workload (current ticket count vs max_tickets)
        3. Consider language match
        4. Prioritize agents with expertise in ticket category
        5. Fall back to round-robin if no perfect match
        
        Returns:
            agent_id or None if no agent available
        """
        if ticket is None:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return None
        
        # Get all active agents
        agents = db.query(User).filter(
            and_(
                User.role.in_([UserRole.agent, UserRole.manager]),
                User.is_active == True,
                User.is_online == True
            )
        ).all()
        
        if not agents:
            # No online agents, get offline ones
            agents = db.query(User).filter(
                and_(
                    User.role.in_([UserRole.agent, UserRole.manager]),
                    User.is_active == True
                )
            ).all()
        
        if not agents:
            return None
        
        # Score each agent
        agent_scores = []
        for agent in agents:
            score = await self._calculate_agent_score(db, agent, ticket)
            agent_scores.append((agent, score))
        
        # Sort by score (descending)
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get best agent
        best_agent = agent_scores[0][0]
        
        return str(best_agent.id)
    
    async def _calculate_agent_score(
        self,
        db: Session,
        agent: User,
        ticket: Ticket
    ) -> float:
        """
        Calculate suitability score for agent
        
        Higher score = better match
        """
        score = 0.0
        
        # 1. Check workload (30 points max)
        current_tickets = db.query(func.count(Ticket.id)).filter(
            and_(
                Ticket.assigned_to == agent.id,
                Ticket.status.notin_(['closed', 'resolved'])
            )
        ).scalar() or 0
        
        workload_percentage = current_tickets / agent.max_tickets if agent.max_tickets > 0 else 1.0
        
        if workload_percentage < 0.5:
            score += 30  # Agent has capacity
        elif workload_percentage < 0.8:
            score += 15  # Agent somewhat busy
        elif workload_percentage < 1.0:
            score += 5   # Agent almost at capacity
        else:
            score -= 20  # Agent over capacity (should still work but penalized)
        
        # 2. Skill match (25 points max)
        if agent.agent_skills:
            skills = [s.strip().lower() for s in agent.agent_skills.split(',')]
            
            # Check if ticket category matches agent skills
            category_match = ticket.category.value.lower() in skills
            if category_match:
                score += 25
            
            # Check if ticket AI tags match agent skills
            if ticket.ai_tags:
                tags = [t.strip().lower() for t in ticket.ai_tags.split(',')]
                matching_tags = set(skills).intersection(set(tags))
                score += len(matching_tags) * 5  # 5 points per matching tag
        
        # 3. Department match (20 points max)
        if agent.department:
            dept = agent.department.lower()
            
            # Map categories to departments
            category_dept_map = {
                'technical': ['technical', 'it', 'engineering'],
                'billing': ['billing', 'finance', 'accounting'],
                'general': ['general', 'support'],
                'bug_report': ['technical', 'qa', 'engineering'],
                'feature_request': ['product', 'engineering'],
                'complaint': ['escalation', 'management']
            }
            
            expected_depts = category_dept_map.get(ticket.category.value, ['general'])
            if any(ed in dept for ed in expected_depts):
                score += 20
        
        # 4. Language match (15 points)
        # Assuming both have language field
        # For now, just check if agent has English (default)
        if agent.language and ticket.creator:
            if agent.language == ticket.creator.language:
                score += 15
        
        # 5. Online status (10 points)
        if agent.is_online:
            score += 10
        
        # 6. Priority handling (bonus points)
        if ticket.priority == TicketPriority.urgent:
            # Prefer managers for urgent tickets
            if agent.role == UserRole.manager:
                score += 15
        
        # 7. Previous success rate (would need to query resolved tickets)
        # TODO: Calculate agent's average resolution time and CSAT score
        
        return score
    
    async def recommend_agents(
        self,
        db: Session,
        ticket: Ticket,
        top_n: int = 3
    ) -> List[Dict[str, any]]:
        """
        Get top N agent recommendations with scores
        
        Returns:
            List of dicts with agent info and matching score
        """
        agents = db.query(User).filter(
            and_(
                User.role.in_([UserRole.agent, UserRole.manager]),
                User.is_active == True
            )
        ).all()
        
        recommendations = []
        
        for agent in agents:
            score = await self._calculate_agent_score(db, agent, ticket)
            
            # Get current workload
            current_tickets = db.query(func.count(Ticket.id)).filter(
                and_(
                    Ticket.assigned_to == agent.id,
                    Ticket.status.notin_(['closed', 'resolved'])
                )
            ).scalar() or 0
            
            recommendations.append({
                "agent_id": str(agent.id),
                "agent_name": agent.full_name,
                "agent_email": agent.email,
                "score": round(score, 2),
                "current_tickets": current_tickets,
                "max_tickets": agent.max_tickets,
                "capacity_percentage": round((current_tickets / agent.max_tickets * 100) if agent.max_tickets > 0 else 100, 1),
                "is_online": agent.is_online,
                "department": agent.department,
                "skills": agent.agent_skills
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:top_n]
    
    async def rebalance_workload(self, db: Session) -> Dict[str, any]:
        """
        Rebalance ticket assignments across agents
        
        Finds overloaded agents and reassigns some tickets to underloaded agents
        
        Returns:
            Dict with reassignment statistics
        """
        # Get all agents with their current workload
        agents = db.query(User).filter(
            and_(
                User.role.in_([UserRole.agent, UserRole.manager]),
                User.is_active == True
            )
        ).all()
        
        agent_workloads = []
        for agent in agents:
            ticket_count = db.query(func.count(Ticket.id)).filter(
                and_(
                    Ticket.assigned_to == agent.id,
                    Ticket.status.notin_(['closed', 'resolved'])
                )
            ).scalar() or 0
            
            agent_workloads.append({
                "agent": agent,
                "ticket_count": ticket_count,
                "capacity": agent.max_tickets,
                "utilization": ticket_count / agent.max_tickets if agent.max_tickets > 0 else 0
            })
        
        # Find overloaded (>90%) and underloaded (<50%) agents
        overloaded = [a for a in agent_workloads if a["utilization"] > 0.9]
        underloaded = [a for a in agent_workloads if a["utilization"] < 0.5]
        
        reassignments = 0
        
        for overloaded_agent_data in overloaded:
            overloaded_agent = overloaded_agent_data["agent"]
            
            # Get some tickets from overloaded agent (low priority first)
            tickets_to_reassign = db.query(Ticket).filter(
                and_(
                    Ticket.assigned_to == overloaded_agent.id,
                    Ticket.status.in_(['open', 'waiting_agent']),
                    Ticket.priority.in_([TicketPriority.low, TicketPriority.medium])
                )
            ).limit(3).all()
            
            for ticket in tickets_to_reassign:
                # Find best underloaded agent
                if underloaded:
                    best_agent_id = await self.assign_best_agent(db, str(ticket.id), ticket)
                    if best_agent_id and best_agent_id != str(overloaded_agent.id):
                        ticket.assigned_to = best_agent_id
                        reassignments += 1
        
        if reassignments > 0:
            db.commit()
        
        return {
            "reassignments": reassignments,
            "overloaded_agents": len(overloaded),
            "underloaded_agents": len(underloaded),
            "message": f"Successfully rebalanced {reassignments} tickets"
        }


# Global routing service instance
routing_service = RoutingService()
