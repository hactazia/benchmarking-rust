/// Fonctions heuristiques utiles pour les problèmes de recherche

/// Distance de Manhattan entre deux points 2D
pub fn manhattan_distance_2d(x1: usize, y1: usize, x2: usize, y2: usize) -> usize {
    x1.abs_diff(x2) + y1.abs_diff(y2)
}

/// Distance euclidienne entre deux points 2D
pub fn euclidean_distance_2d(x1: usize, y1: usize, x2: usize, y2: usize) -> f64 {
    let dx = x1 as f64 - x2 as f64;
    let dy = y1 as f64 - y2 as f64;
    (dx * dx + dy * dy).sqrt()
}

/// Distance de Chebyshev (diagonale autorisée)
pub fn chebyshev_distance(x1: usize, y1: usize, x2: usize, y2: usize) -> usize {
    x1.abs_diff(x2).max(y1.abs_diff(y2))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_manhattan() {
        assert_eq!(manhattan_distance_2d(0, 0, 3, 4), 7);
        assert_eq!(manhattan_distance_2d(5, 5, 5, 5), 0);
    }

    #[test]
    fn test_euclidean() {
        assert_eq!(euclidean_distance_2d(0, 0, 3, 4), 5.0);
    }
}
