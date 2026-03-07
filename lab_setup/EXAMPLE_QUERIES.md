# Example Queries for Neo4j Aura Agent

Example natural language questions to ask the **Aircraft Digital Twin Analyst** agent in Neo4j Aura. Questions are grouped by the agent tool they exercise.

---

## Cypher Template Questions

These questions map to the pre-built Cypher template tools configured on the agent.

### Aircraft Systems, Components, and Sensors

- "Tell me about aircraft N95040A"
- "What systems does aircraft N30268B have?"
- "Show all sensors on aircraft N54980C"
- "What components are in the CFM56-7B engines?"
- "List all Boeing 737-800 aircraft in the fleet"
- "Which aircraft are operated by ExampleAir?"
- "How many components does each system have on N95040A?"

### Aircraft Maintenance Events

- "Show the maintenance summary for N54980C"
- "What critical maintenance events have been reported for N95040A?"
- "List all bearing wear faults across the fleet"
- "Which aircraft have had overheat events on their engines?"
- "Show recent maintenance events for SkyWays aircraft"
- "What corrective actions were taken for vibration exceedance faults?"

### Aircraft Component Removals

- "What component removals have occurred on N95040A?"
- "Show all removals due to contamination"
- "Which components have been removed with the highest flight cycles?"
- "List component removals for Boeing 737-800 aircraft"

### Aircraft Flight Details

- "Show flights operated by aircraft N95040A"
- "What flights depart from JFK?"
- "Which flights were delayed and why?"
- "What are the top routes by flight count?"
- "Show delayed arrivals at LAX"
- "Which aircraft has the most flights with weather delays?"

### Sensor Operating Limits with Source

- "What are the sensor operating limits for N30268B?"
- "What is the maximum EGT allowed for the A320-200?"
- "Show the vibration limits for all Boeing 737-800 sensors"
- "What operating limits are defined for N1Speed sensors?"
- "What maintenance manual defines the fuel flow limits for the A321neo?"

---

## Text2Cypher Questions

These questions require the agent to generate Cypher on the fly. They go beyond what the templates cover.

### Maintenance Analysis

- "Which aircraft has the most critical maintenance events?"
- "What are the most common fault types across the fleet?"
- "How many maintenance events are there by severity level?"
- "Which components have the highest failure rate?"
- "What faults do aircraft N95040A and N26760M share?"
- "Show all aircraft that had both overheat and vibration exceedance faults"
- "Which engine systems have the most maintenance events?"
- "What is the ratio of critical to minor maintenance events per aircraft model?"

### Flight & Delay Analysis

- "What are the top causes of flight delays?"
- "Which airports have the most delayed arrivals?"
- "How many flights were delayed due to maintenance issues?"
- "What is the average delay time by cause?"
- "Which operator has the most weather-related delays?"
- "Show flights that were delayed more than 60 minutes"
- "Which routes have the highest delay frequency?"

### Topology & Structure

- "Show all components in the hydraulics system"
- "How many sensors are attached to each engine type?"
- "Which aircraft models have the most components?"
- "List all Airbus aircraft with their system counts"
- "What is the complete system hierarchy for the Embraer E190?"

### Cross-Domain (Graph Traversal)

- "Which sensors have operating limits defined?"
- "Trace the provenance of the EGT operating limit for B737-800"
- "Which maintenance manuals apply to Airbus aircraft?"
- "Show operating limits that were extracted from the A320-200 maintenance manual"
- "Which aircraft have sensors with operating limits that exceed fleet averages?"
- "Find aircraft where maintenance events occurred on components connected to EGT sensors"

---

## Similarity Search Questions

These use the vector index over maintenance manual chunks to find semantically relevant content.

### Troubleshooting

- "How do I troubleshoot engine vibration?"
- "What are the procedures for an EGT exceedance event?"
- "How do I diagnose a fuel flow anomaly?"
- "What should I check if hydraulic pressure drops?"
- "What are the steps for compressor stall recovery?"

### Operating Limits & Parameters

- "What are the EGT limits during takeoff?"
- "What is the normal vibration range for cruise operations?"
- "What N1 speed limits apply during climb?"
- "What fuel flow rates are expected at idle?"

### Scheduled Maintenance

- "What is the engine inspection schedule?"
- "When should the hydraulic system be serviced?"
- "What are the routine maintenance intervals for the avionics suite?"
- "What lubrication procedures are required for engine bearings?"

### Component-Specific

- "What are the turbine blade inspection criteria?"
- "How often should the combustion chamber be inspected?"
- "What are the filter replacement intervals for the hydraulic system?"
- "What are the known failure modes for the low-pressure compressor?"
