use crate::algorithms::Problem;
use rand::seq::SliceRandom;
use rand::thread_rng;
use std::fmt;

#[derive(Clone)]
pub struct Taquin {
    size: usize,
    initial_state: Vec<u8>,
    goal_state: Vec<u8>,
    heuristic_type: HeuristicType,
}

#[derive(Clone, Copy, Debug)]
pub enum HeuristicType {
    Manhattan,
    Hamming,
    None,
}

impl Taquin {
    pub fn initial_state_string(&self) -> String {
        let mut result = String::new();
        for (i, &val) in self.initial_state.iter().enumerate() {
            if i > 0 && i % self.size == 0 {
                result.push('\n');
            }
            result.push_str(&format!("{:3}", val));
        }
        result
    }

    pub fn new(size: usize, heuristic: HeuristicType) -> Self {
        let goal_state: Vec<u8> = (0..(size * size) as u8).collect();

        Taquin {
            size,
            initial_state: goal_state.clone(),
            goal_state,
            heuristic_type: heuristic,
        }
    }

    pub fn generate_random(&mut self, moves: usize) {
        let mut current = self.goal_state.clone();
        let mut rng = thread_rng();

        for _ in 0..moves {
            let successors = self.get_successors(&current);
            if let Some((next_state, _)) = successors.choose(&mut rng) {
                current = next_state.clone();
            }
        }

        self.initial_state = current;
    }

    pub fn from_state(size: usize, state: Vec<u8>, heuristic: HeuristicType) -> Self {
        let goal_state: Vec<u8> = (0..(size * size) as u8).collect();

        Taquin {
            size,
            initial_state: state,
            goal_state,
            heuristic_type: heuristic,
        }
    }

    fn find_blank(&self, state: &[u8]) -> usize {
        state.iter().position(|&x| x == 0).unwrap()
    }

    fn get_successors(&self, state: &[u8]) -> Vec<(Vec<u8>, usize)> {
        let blank = self.find_blank(state);
        let row = blank / self.size;
        let col = blank % self.size;
        let mut successors = Vec::new();

        if row > 0 {
            let mut new_state = state.to_vec();
            let swap_pos = (row - 1) * self.size + col;
            new_state.swap(blank, swap_pos);
            successors.push((new_state, 1));
        }

        if row < self.size - 1 {
            let mut new_state = state.to_vec();
            let swap_pos = (row + 1) * self.size + col;
            new_state.swap(blank, swap_pos);
            successors.push((new_state, 1));
        }

        if col > 0 {
            let mut new_state = state.to_vec();
            let swap_pos = row * self.size + (col - 1);
            new_state.swap(blank, swap_pos);
            successors.push((new_state, 1));
        }

        if col < self.size - 1 {
            let mut new_state = state.to_vec();
            let swap_pos = row * self.size + (col + 1);
            new_state.swap(blank, swap_pos);
            successors.push((new_state, 1));
        }

        successors
    }

    fn manhattan_distance(&self, state: &[u8]) -> usize {
        let mut distance = 0;

        for (i, &tile) in state.iter().enumerate() {
            if tile == 0 {
                continue;
            }

            let current_row = i / self.size;
            let current_col = i % self.size;
            let goal_pos = tile as usize;
            let goal_row = goal_pos / self.size;
            let goal_col = goal_pos % self.size;

            distance += current_row.abs_diff(goal_row) + current_col.abs_diff(goal_col);
        }

        distance
    }

    fn hamming_distance(&self, state: &[u8]) -> usize {
        state
            .iter()
            .enumerate()
            .filter(|(i, &tile)| tile != 0 && tile as usize != *i)
            .count()
    }
}

impl Problem for Taquin {
    type State = Vec<u8>;

    fn initial_state(&self) -> Self::State {
        self.initial_state.clone()
    }

    fn is_goal(&self, state: &Self::State) -> bool {
        state == &self.goal_state
    }

    fn successors(&self, state: &Self::State) -> Vec<(Self::State, usize)> {
        self.get_successors(state)
    }

    fn heuristic(&self, state: &Self::State) -> usize {
        match self.heuristic_type {
            HeuristicType::Manhattan => self.manhattan_distance(state),
            HeuristicType::Hamming => self.hamming_distance(state),
            HeuristicType::None => 0,
        }
    }

    fn description(&self) -> String {
        format!(
            "Taquin {}x{} - Heuristique: {:?}",
            self.size, self.size, self.heuristic_type
        )
    }
}

impl fmt::Display for Taquin {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "Taquin {}x{}", self.size, self.size)?;
        writeln!(f, "État initial:")?;

        for row in 0..self.size {
            for col in 0..self.size {
                let tile = self.initial_state[row * self.size + col];
                if tile == 0 {
                    write!(f, "   ")?;
                } else {
                    write!(f, "{:2} ", tile)?;
                }
            }
            writeln!(f)?;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_taquin_3x3() {
        let taquin = Taquin::new(3, HeuristicType::Manhattan);
        assert_eq!(taquin.initial_state.len(), 9);
        assert!(taquin.is_goal(&taquin.goal_state));
    }

    #[test]
    fn test_manhattan_distance() {
        let taquin = Taquin::new(3, HeuristicType::Manhattan);
        let goal_state = vec![0, 1, 2, 3, 4, 5, 6, 7, 8];
        assert_eq!(taquin.manhattan_distance(&goal_state), 0);

        let state = vec![1, 0, 2, 3, 4, 5, 6, 7, 8];
        assert_eq!(taquin.manhattan_distance(&state), 1);
    }

    #[test]
    fn test_successors() {
        let state = vec![1, 2, 3, 4, 0, 5, 6, 7, 8];
        let taquin = Taquin::from_state(3, state.clone(), HeuristicType::Manhattan);
        let successors = taquin.get_successors(&state);
        assert_eq!(successors.len(), 4);
    }
}
