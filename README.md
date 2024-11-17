# parimutuel-py
A python script that implements the basics of pari mutuel betting

1. Basic Concept:
   - "Pari-mutuel" comes from French, meaning "mutual betting"
   - All bets of a particular type are placed together in a pool
   - After taking out the house commission (takeout), the remaining pool is shared proportionally among winning bettors
   - Most commonly used in horse racing, but also in other sports betting

2. Key Characteristics:
   - The final payoff odds are not determined until betting is closed
   - Odds change dynamically based on how much is bet on each outcome
   - The house has no risk as they take a fixed commission
   - Returns are determined by other bettors' actions, not by the house

3. How Odds Work:
   - Odds are calculated by dividing the total pool by the amount bet on each outcome
   - The more money bet on an outcome, the lower its odds become
   - Conversely, less popular outcomes offer higher potential returns

4. Code Breakdown:

   a. Pool Management:
   ```python
   self.total_pool: float = 0
   self.outcomes: Dict[str, float] = {}
   ```
   - Tracks all money in the betting pool
   - Maintains separate totals for each outcome

   b. Dynamic Odds Calculation:
   ```python
   def calculate_odds(self) -> Dict[str, float]:
       odds = {}
       for outcome, total_bet in self.outcomes.items():
           if total_bet > 0:
               implied_prob = total_bet / self.total_pool
               odds[outcome] = (1 / implied_prob) - 1
   ```
   - Continuously updates odds based on betting distribution
   - Converts implied probabilities to decimal odds

   c. Payout Calculation:
   ```python
   winning_pool = self.total_pool * (1 - self.house_commission)
   payout_per_unit = winning_pool / self.outcomes[winning_outcome]
   ```
   - Removes house commission from total pool
   - Distributes remaining pool proportionally among winners

   d. Bet Tracking:
   ```python
   @dataclass
   class Bet:
       player_id: str
       outcome: str
       amount: float
       timestamp: datetime
       odds_at_time: float
   ```
   - Records individual bets with timestamps
   - Stores odds at time of bet for reference


