***Author: Patrick Singh***

# BEPIS - Epsilon-Differential-Privacy for Graph Databases

BEPIS is an experimental approach for realizing **Epsilon-Differential-Privacy** as a data anonymization technique for graph databases, specifically targeting Neo4j. The system provides a privacy-preserving interface that allows users to query sensitive graph data while maintaining formal privacy guarantees.

## 🔒 Privacy Mechanism

BEPIS implements the **sensitivity-based mechanism** with **elastic sensitivity** as an upper boundary to local sensitivity. The system applies a smoothing function on top of local sensitivity to ensure a certain distance to the true database, providing robust privacy protection even against sophisticated attacks.

## ✨ Key Features

- **Console Interface**: Interactive command-line interface to running Neo4j graph instances
- **CSV Data Loading**: Streamlined data ingestion from CSV files into the graph database
- **Query Translation**: Automatic translation of user queries to privacy-preserving equivalents
- **Aggregation Support**: Focus on aggregation queries, particularly counting operations
- **Elastic Sensitivity**: Advanced sensitivity analysis with smoothing functions
- **Experimental Framework**: First-steps implementation for research and development

## 🏗️ Architecture

### Core Components

1. **Privacy Engine**: Implements ε-differential privacy mechanisms
2. **Query Translator**: Converts standard queries to privacy-preserving versions
3. **Sensitivity Calculator**: Computes local and elastic sensitivity bounds
4. **Smoothing Layer**: Applies noise calibration based on sensitivity analysis
5. **Neo4j Interface**: Direct integration with Neo4j graph database

### Privacy Guarantees

- **Epsilon-Differential Privacy**: Formal privacy protection with configurable ε parameters
- **Local Sensitivity**: Dynamic sensitivity calculation per query
- **Elastic Sensitivity**: Upper bound mechanism for enhanced privacy
- **Smoothing Functions**: Distance-based privacy amplification

## 🚀 Quick Start

### Prerequisites

- Neo4j database instance (running)
- Python 3.8+
- Required Python packages (see `requirements.txt`)

### Installation

```bash
git clone https://github.com/yourusername/bepis.git
cd bepis
pip install -r requirements.txt
```

### Basic Usage

```bash
# Start BEPIS console
python bepis.py --neo4j-uri bolt://localhost:7687

# Load data from CSV
BEPIS> load_data --file dataset.csv --epsilon 1.0

# Execute privacy-preserving count query
BEPIS> count_nodes --label Person --epsilon 0.5
```

## 📊 Supported Query Types

Currently, BEPIS focuses on **aggregation queries** with plans to expand:

- ✅ **Count Queries**: Node and relationship counting with noise injection
- ✅ **Basic Aggregations**: Sum, average with differential privacy
- 🚧 **Graph Statistics**: Degree distributions, clustering coefficients
- 🚧 **Subgraph Queries**: Privacy-preserving subgraph analysis

## 🔬 Research Context

This project represents **experimental, first-steps** into applying differential privacy to graph databases. The implementation serves as a research prototype for:

- Understanding privacy-utility trade-offs in graph data
- Developing robust sensitivity analysis for graph queries
- Exploring smoothing techniques for enhanced privacy
- Building foundations for production-ready graph privacy systems

## ⚙️ Configuration

### Privacy Parameters

```python
# Example configuration
EPSILON = 1.0              # Privacy budget
DELTA = 1e-6              # Relaxation parameter
SMOOTHING_FACTOR = 2.0    # Elastic sensitivity multiplier
MAX_SENSITIVITY = 100     # Upper bound for sensitivity
```

### Database Connection

```python
# Neo4j connection settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
```

## 📈 Performance Considerations

- **Query Complexity**: Linear increase in computation time for privacy mechanisms
- **Memory Usage**: Additional overhead for sensitivity calculations
- **Accuracy**: Trade-off between privacy (lower ε) and query accuracy
- **Scalability**: Performance testing on graphs up to 1M nodes

## 🛠️ Development

### Project Structure

```
bepis/
├── src/
│   ├── privacy/          # Core privacy mechanisms
│   ├── query/            # Query translation layer
│   ├── sensitivity/      # Sensitivity analysis
│   └── database/         # Neo4j interface
├── tests/                # Unit and integration tests
├── examples/             # Usage examples and demos
└── docs/                 # Technical documentation
```

### Running Tests

```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests (requires Neo4j)
python -m pytest tests/integration/

# Privacy guarantee verification
python -m pytest tests/privacy/
```

## 📚 Technical References

- **Differential Privacy**: Dwork, C. (2006). "Differential Privacy"
- **Local Sensitivity**: Nissim, K., et al. (2007). "Smooth sensitivity and sampling"
- **Graph Privacy**: Hay, M., et al. (2009). "Accurate estimation of the degree distribution"

## ⚠️ Limitations & Future Work

### Current Limitations
- Limited to aggregation queries
- Single-threaded query processing
- Basic smoothing functions
- Experimental sensitivity bounds

### Planned Enhancements
- Extended query support (path queries, pattern matching)
- Distributed privacy mechanisms
- Advanced smoothing techniques
- Real-world privacy auditing tools

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution
- New query types and privacy mechanisms
- Performance optimizations
- Privacy analysis tools
- Documentation and examples

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Contact

**Patrick Singh**
- Email: [your.email@domain.com]
- GitHub: [@yourusername]
- Research Profile: [link to academic profile]

---

**Disclaimer**: This is an experimental research prototype. Use in production environments requires additional privacy auditing and security considerations.
