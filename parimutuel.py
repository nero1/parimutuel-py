from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BettingStatus(Enum):
    """Status states for the betting round"""
    OPEN = "open"
    CLOSED = "closed"
    SETTLED = "settled"

@dataclass
class Bet:
    """Class to store individual bet information"""
    player_id: str
    outcome: str
    amount: float
    timestamp: datetime
    odds_at_time: float

class BettingError(Exception):
    """Custom exception for betting-related errors"""
    pass

class ParimutuelSystem:
    def __init__(self, 
                 house_commission: float = 0.15, 
                 minimum_bet: float = 1.0,
                 maximum_bet: Optional[float] = None):
        """
        Initialize the Parimutuel betting system
        
        Args:
            house_commission: Percentage taken by the house (default 15%)
            minimum_bet: Minimum allowed bet amount
            maximum_bet: Maximum allowed bet amount (None for no limit)
        """
        if not 0 <= house_commission < 1:
            raise ValueError("House commission must be between 0 and 1")
            
        self.house_commission = house_commission
        self.minimum_bet = minimum_bet
        self.maximum_bet = maximum_bet
        self.reset_betting_round()
        
    def reset_betting_round(self):
        """Reset all betting data for a new round"""
        self.bets: Dict[str, List[Bet]] = {}  # Outcome: List of bets
        self.total_pool: float = 0
        self.status = BettingStatus.OPEN
        self.outcomes: Dict[str, float] = {}  # Outcome: Total amount
        self.winning_outcome: Optional[str] = None
        
    def validate_bet(self, amount: float, outcome: str) -> None:
        """
        Validate a bet meets all requirements
        
        Args:
            amount: Bet amount to validate
            outcome: Outcome to validate
        
        Raises:
            BettingError: If bet is invalid
        """
        if self.status != BettingStatus.OPEN:
            raise BettingError("Betting is not currently open")
            
        if amount < self.minimum_bet:
            raise BettingError(f"Bet amount below minimum of {self.minimum_bet}")
            
        if self.maximum_bet and amount > self.maximum_bet:
            raise BettingError(f"Bet amount above maximum of {self.maximum_bet}")
            
        if outcome not in self.outcomes and len(self.outcomes) > 0:
            raise BettingError("Invalid outcome selection")
            
    def add_outcome(self, outcome: str) -> None:
        """
        Add a valid outcome to bet on
        
        Args:
            outcome: Name of the outcome
        """
        if self.status != BettingStatus.OPEN:
            raise BettingError("Cannot add outcomes after betting has started")
            
        self.outcomes[outcome] = 0
        self.bets[outcome] = []
        
    def place_bet(self, player_id: str, outcome: str, amount: float) -> Tuple[float, float]:
        """
        Place a bet in the system
        
        Args:
            player_id: Unique identifier for the player
            outcome: The outcome being bet on
            amount: Amount being bet
            
        Returns:
            Tuple of (current_odds, total_pool)
        """
        # Validate the bet
        self.validate_bet(amount, outcome)
        
        # Calculate current odds before adding new bet
        current_odds = self.calculate_odds()[outcome]
        
        # Create and record the bet
        bet = Bet(
            player_id=player_id,
            outcome=outcome,
            amount=amount,
            timestamp=datetime.now(),
            odds_at_time=current_odds
        )
        
        self.bets[outcome].append(bet)
        self.outcomes[outcome] += amount
        self.total_pool += amount
        
        logger.info(f"Bet placed: {player_id} bet {amount} on {outcome}")
        return current_odds, self.total_pool
        
    def calculate_odds(self) -> Dict[str, float]:
        """
        Calculate current odds for all outcomes
        
        Returns:
            Dictionary of outcomes and their current odds
        """
        odds = {}
        for outcome, total_bet in self.outcomes.items():
            if total_bet > 0:
                # Calculate implied probability then convert to decimal odds
                implied_prob = total_bet / self.total_pool if self.total_pool > 0 else 0
                odds[outcome] = (1 / implied_prob) - 1 if implied_prob > 0 else float('inf')
            else:
                odds[outcome] = float('inf')
        return odds
    
    def close_betting(self) -> None:
        """Close betting for this round"""
        if self.status != BettingStatus.OPEN:
            raise BettingError("Betting is not open")
        self.status = BettingStatus.CLOSED
        logger.info("Betting closed for this round")
        
    def calculate_payouts(self, winning_outcome: str) -> Dict[str, float]:
        """
        Calculate payouts for a winning outcome
        
        Args:
            winning_outcome: The outcome that won
            
        Returns:
            Dictionary of player_id: payout_amount
        """
        if self.status != BettingStatus.CLOSED:
            raise BettingError("Betting must be closed before calculating payouts")
            
        if winning_outcome not in self.outcomes:
            raise BettingError("Invalid winning outcome")
            
        self.winning_outcome = winning_outcome
        payouts = {}
        
        # Calculate winning pool after house commission
        winning_pool = self.total_pool * (1 - self.house_commission)
        
        # If no bets on winner, house keeps everything
        if self.outcomes[winning_outcome] == 0:
            logger.info("No winning bets placed")
            return payouts
            
        # Calculate payout ratio
        payout_per_unit = winning_pool / self.outcomes[winning_outcome]
        
        # Calculate individual payouts
        for bet in self.bets[winning_outcome]:
            payouts[bet.player_id] = bet.amount * payout_per_unit
            
        self.status = BettingStatus.SETTLED
        return payouts
    
    def get_betting_statistics(self) -> Dict[str, any]:
        """
        Get current betting statistics
        
        Returns:
            Dictionary containing betting statistics
        """
        return {
            "total_pool": self.total_pool,
            "number_of_bets": sum(len(bets) for bets in self.bets.values()),
            "odds": self.calculate_odds(),
            "status": self.status.value,
            "outcome_totals": self.outcomes.copy(),
            "house_commission": self.house_commission
        }

# Example usage
def demo_enhanced_betting():
    # Initialize system
    betting = ParimutuelSystem(house_commission=0.15, minimum_bet=5.0, maximum_bet=1000.0)
    
    # Add possible outcomes
    betting.add_outcome("Horse1")
    betting.add_outcome("Horse2")
    betting.add_outcome("Horse3")
    
    try:
        # Place various bets
        betting.place_bet("Player1", "Horse1", 100.0)
        betting.place_bet("Player2", "Horse2", 200.0)
        betting.place_bet("Player3", "Horse1", 150.0)
        betting.place_bet("Player4", "Horse3", 50.0)
        
        # Show betting statistics
        print("\nCurrent betting statistics:")
        stats = betting.get_betting_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Close betting and calculate payouts
        betting.close_betting()
        payouts = betting.calculate_payouts("Horse1")
        
        print("\nPayouts:")
        for player, amount in payouts.items():
            print(f"{player}: ${amount:.2f}")
            
    except BettingError as e:
        print(f"Betting error occurred: {e}")

if __name__ == "__main__":
    demo_enhanced_betting()
