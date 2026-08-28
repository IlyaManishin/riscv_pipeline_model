# Branch Unit Placement Research

## Background

The project contains two implementations of the same microarchitecture:

* Python cycle-accurate pipeline model
* RTL implementation

Initially, branch resolution was performed in the **Decode** stage in both implementations.

During timing analysis of the RTL design, a critical path was identified in the decode stage. The path was mainly related to:

* branch condition evaluation (`br_unit`)
* target address calculation for `JAL` instructions (`PC + immediate`)

One possible solution was to move branch processing from **Decode** to **Execute**. This would shorten the critical path and improve maximum frequency. However, it would also increase the control hazard penalty by one cycle.

The goal of this research was to determine which option provides better overall performance.

---

## Problem

At the time of the research, forwarding had not yet been implemented.

A direct comparison of CPI between the two architectures would therefore be misleading because the current pipeline relied on stalls for all RAW dependencies. After forwarding is added, CPI is expected to change significantly.

As a result, the architectural decision had to be made based on the expected future design rather than the current implementation.

---

## Methodology

Pipeline statistics were collected from the Python model using several benchmark programs.

The collected metrics included:

* instruction count
* cycle count
* branch and jump statistics
* control hazards
* RAW hazards
* stall counts

Using these statistics, the expected CPI of a pipeline with forwarding was estimated.

The following assumptions were made:

1. RAW hazards eliminated by forwarding were removed from the total cycle count.
2. Control hazard penalties remained unchanged for the Decode-stage branch unit design.
3. For the Execute-stage branch unit design, an additional cycle penalty was added for every control hazard that would be resolved one stage later.
4. The same approach was applied to `JAL` instructions because the `PC + immediate` calculation also contributes to the decode-stage critical path.

This allowed estimation of CPI for both architectural options without implementing forwarding.

---

## Results

### Estimated CPI with forwarding

Branch resolution in Decode:

* Typical CPI ≈ 1.6 - 1.7

Branch resolution in Execute:

* Typical CPI ≈ 1.7 - 1.8

The Decode-stage design showed a slightly better CPI because control hazards were resolved earlier.

### Estimated Frequency

RTL timing analysis produced the following results:

| Configuration          | Estimated Frequency |
| ---------------------- | ------------------- |
| Branch unit in Decode  | ~127 MHz            |
| Branch unit in Execute | ~141 MHz            |

Moving branch processing to Execute improved the maximum frequency by approximately 11%.

---

## Performance Evaluation

Although the Execute-stage design has a slightly worse CPI, the frequency improvement is larger than the CPI degradation.

As a result, overall execution time is reduced for most workloads.

The comparison indicates that the higher operating frequency compensates for the additional control hazard penalty.

---

## Conclusion

The research shows that moving branch processing from **Decode** to **Execute** is the preferred architectural choice.

Key reasons:

* Significant reduction of the decode-stage critical path.
* Increase in maximum frequency from approximately **127 MHz** to **141 MHz**.
* Only a small CPI increase after accounting for forwarding.
* Better overall performance despite the additional control hazard penalty.

Based on these results, future development should target a pipeline where:

* branch resolution is performed in the **Execute** stage;
* forwarding is implemented to eliminate most RAW stalls;
* control hazards are handled using the increased Execute-stage penalty.
