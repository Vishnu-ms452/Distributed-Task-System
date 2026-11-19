# Distributed Task Management System using TCP Sockets and SDN

A distributed task execution system that connects a central Task Manager with four Worker nodes using TCP socket programming, supported by an SDN-controlled network built with Mininet, Open vSwitch and OS-Ken.

## Overview

The project demonstrates how computational tasks can be distributed across multiple worker nodes while maintaining reliable communication and network connectivity.

The Task Manager accepts tasks, manages worker connections, distributes work and collects results. The network infrastructure is emulated using Mininet and managed through an OS-Ken SDN controller.

The system also explores worker load balancing, task recovery after worker disconnection, and network resilience using the Spanning Tree Protocol (STP).

## Architecture

The project has two main layers:

**Application layer**
- **Task Manager:** Central server responsible for worker registration, task management, task assignment and result collection.
- **Workers:** Four independent nodes that receive and execute computational tasks.
- **TCP communication:** Provides reliable communication between the manager and workers.
- **Scheduler:** Implements Least-Loaded Scheduling for worker selection and supports comparison with Round-Robin scheduling.

**SDN and network layer**
- **Mininet:** Emulates the virtual network.
- **Open vSwitch:** Provides virtual Layer 2 switching.
- **OS-Ken:** Controls the switches through OpenFlow 1.3.
- **STP:** Prevents switching loops and manages redundant links.

## Network Topology

The main Mininet topology contains:

| Component | Configuration |
|---|---|
| Task Manager | 1 host (h1) |
| Workers | 4 hosts (h2–h5) |
| Switches | 2 Open vSwitch switches (s1, s2) |
| Inter-switch connections | 2 redundant links |
| Controller | OS-Ken |
| Southbound protocol | OpenFlow 1.3 |

### IP Addressing

| Host | Role | IP Address |
|---|---|---|
| h1 | Task Manager | 10.0.0.1 |
| h2 | Worker W1 | 10.0.0.2 |
| h3 | Worker W2 | 10.0.0.3 |
| h4 | Worker W3 | 10.0.0.4 |
| h5 | Worker W4 | 10.0.0.5 |

The Task Manager and Workers communicate through the Mininet switches. The SDN controller manages packet forwarding and STP independently of application-level task scheduling.

## Features

- TCP client-server communication using Python sockets.
- Multiple worker connections handled using threads.
- Worker registration using unique identifiers.
- Task submission and automated distribution.
- Computational operations: sum, multiplication, maximum and minimum.
- JSON-based message exchange using newline-delimited framing.
- Task result collection and status tracking.
- Re-queuing of unfinished tasks after worker disconnection.
- Least-Loaded and Round-Robin scheduling evaluation.
- SDN-based packet forwarding using OpenFlow 1.3.
- STP-based loop prevention and redundant-link handling.
- Network connectivity and failure-scenario testing.

## Technology Stack

| Technology | Usage |
|---|---|
| Python | Application and scheduling implementation |
| TCP Sockets | Manager-worker communication |
| JSON | Message exchange |
| Multithreading | Concurrent worker connections |
| Mininet | Network emulation |
| Open vSwitch | Virtual switching |
| OS-Ken | SDN controller |
| OpenFlow 1.3 | Switch-controller communication |
| STP | Loop prevention |
| Ubuntu | Development environment |

## Repository Structure

```text
CN-Jack/
│
├── src/
│   ├── task_manager.py
│   ├── worker.py
│   ├── protocol.py
│   └── scheduler.py
│
├── sdn/
│   ├── topology.py
│   ├── topology_4workers.py
│   ├── simple_switch.py
│   └── dynamic_stp.py
│
├── tests/
│   ├── test_scheduler.py
│   └── uneven_load_test.py
│
├── benchmarks/
│   ├── benchmark.py
│   └── benchmark_results.csv
│
└── README.md
```

### Directory Description

| Directory | Contents |
|---|---|
| `src/` | Task Manager, Worker, TCP communication protocol and scheduler |
| `sdn/` | Mininet topologies and OS-Ken controller applications |
| `tests/` | Scheduler unit tests and uneven-load testing |
| `benchmarks/` | Scheduling benchmark implementation and results |

## Getting Started

### Prerequisites

The project is developed for Ubuntu Linux and requires:

- Python 3
- Mininet
- Open vSwitch
- OS-Ken
- OpenFlow 1.3 support

The application-layer implementation primarily uses Python standard libraries.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CN-Jack
```

### 2. Start the SDN Controller

Open a terminal in the project directory:

```bash
osken-manager sdn/dynamic_stp.py
```

This starts the OS-Ken controller with the dynamic STP application.

### 3. Start the Mininet Topology

Open another terminal:

```bash
sudo python3 sdn/topology_4workers.py
```

This creates the two-switch, four-worker topology with redundant inter-switch links.

### 4. Verify Network Connectivity

Inside the Mininet CLI:

```text
nodes
net
links
pingall
```

`pingall` checks connectivity between all virtual hosts.

### 5. Start the Task Manager and Workers

Open terminals for the Mininet hosts:

```text
xterm h1 h2 h3 h4 h5
```

In the h1 terminal, start the Task Manager:

```bash
cd /path/to/CN-Jack/src
python3 task_manager.py
```

In the h2 terminal:

```bash
cd /path/to/CN-Jack/src
python3 worker.py --host 10.0.0.1 --id W1
```

In the h3 terminal:

```bash
cd /path/to/CN-Jack/src
python3 worker.py --host 10.0.0.1 --id W2
```

In the h4 terminal:

```bash
cd /path/to/CN-Jack/src
python3 worker.py --host 10.0.0.1 --id W3
```

In the h5 terminal:

```bash
cd /path/to/CN-Jack/src
python3 worker.py --host 10.0.0.1 --id W4
```

Replace `/path/to/CN-Jack` with the actual absolute path to the cloned repository.

### 6. Submit Tasks

In the Task Manager terminal, submit computational tasks:

```text
add sum 1 2 3
add multiply 2 3 4
add max 4 8 1
add min 10 5 2
```

Useful commands:

```text
workers
tasks
help
quit
```

## Testing and Performance Evaluation

The project includes separate testing and benchmarking components.

### Scheduler Testing

The test suite evaluates:
- Worker selection.
- Workload tracking.
- Failed-worker handling.
- Task completion and workload updates.
- Worker recovery.

Run the scheduler tests from the project root:

```bash
python3 -m unittest discover -s tests -v
```

### Scheduling Benchmark

The scheduling benchmark compares Least-Loaded Scheduling and Round-Robin Scheduling using 1,000 simulated tasks over five trials.

Run:

```bash
python3 benchmarks/benchmark.py
```

The generated CSV contains the scheduling results.

### Live System Benchmark

The final project demonstration also evaluates 10,000 tasks across four Mininet workers, including a worker-disconnection scenario.

Reported results:

| Metric | Normal benchmark | Worker failure benchmark |
|---|---:|---:|
| Tasks submitted | 10,000 | 10,000 |
| Tasks completed | 10,000 | 10,000 |
| Failed tasks | 0 | 0 |
| Execution time | 16.147 s | 20.629 s |
| Throughput | 619.31 tasks/s | 484.75 tasks/s |

The separate scheduling simulation reported a 20.16% reduction in simulated makespan for Least-Loaded Scheduling compared with Round-Robin Scheduling.

**Note:** Simulated scheduling makespan and live Mininet benchmark performance are different measurements.

## Fault Tolerance

The project examines two failure scenarios:

**Worker failure**
- The Task Manager detects worker disconnection.
- Unfinished tasks are returned to the pending queue.
- Tasks can be assigned to another available worker.

**Network link failure**
- STP manages redundant switch links.
- The controller handles topology changes and port states.
- An alternative forwarding path can be enabled when available.

These mechanisms address application-level task recovery and network-level resilience separately.

## Project Documentation

The detailed project report contains:
- Problem statement and objectives.
- System architecture and workflow.
- TCP socket implementation.
- Mininet and SDN implementation.
- Socket–SDN integration.
- Testing and demonstration screenshots.
- Failure handling and performance evaluation.
- Results and conclusion.

## Future Scope

- Extend the topology to support additional workers and switches.
- Improve scheduling strategies for larger workloads.
- Introduce stronger worker failure detection.
- Add authentication and encrypted communication.
- Evaluate performance under different network conditions.

## Team

**Department of Artificial Intelligence and Machine Learning**  
PES University

- Bhoomika U Harige
- Vishnu Marangat Sankaran
- Badarinath S Kini

**Academic Year:** 2026–2027

---

*This project was developed as part of the Computer Networks Mini Project.*
