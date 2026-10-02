# Domain-specific review gates

## Contents

- [Shared gate pattern](#shared-gate-pattern)
- [Chemistry](#chemistry)
- [Engineering](#engineering)
- [Materials Science](#materials-science)
- [Atmospheric Science](#atmospheric-science)
- [Climate Ecology](#climate-ecology)
- [Hydrology](#hydrology)
- [Remote Sensing and Earth Observation](#remote-sensing-and-earth-observation)


Use this file only after the shared manuscript fact base is clear. These gates are
claim-dependent stress tests inside `nature-reviewer`; they do not create specialist
reviewer identities and do not replace the source-grounded Nature axes.

Apply only the domain sections triggered by the manuscript. Convert the diagnostics
into normal reviewer prose. Do not expose gate names, routing tables, pattern IDs, or
this file's internal structure in the final report.

## Shared gate pattern

For each central claim, identify:

- the claimed contribution and its exact scope;
- the evidence chain needed to support that claim;
- the assumptions, controls, uncertainty, and alternative explanations that carry the
  conclusion;
- whether the supplied material directly demonstrates the claim or only a narrower
  finding;
- what revision would either strengthen the evidence or calibrate the claim.

Make a concern major only when it affects the central contribution or the reader's
confidence in the evidence chain. Use minor comments for terminology, local clarity,
figure/table presentation, or non-central reporting gaps.

## Chemistry

Use for manuscripts where claims depend on synthesis, reaction development, catalysis,
chemical biology, analytical chemistry, spectroscopy, electrochemistry, computational
chemistry, or chemically specific materials/interfacial mechanisms.

Stress-test:

- identity, purity, structure, speciation, aggregation, and analytical quantification;
- reaction scope, selectivity, controls, yields, product balance, and boundary
  conditions;
- catalytic metrics such as turnover, quantum/Faradaic efficiency, stability,
  mass transport, light absorption, reference calibration, and normalization;
- whether mechanistic claims distinguish correlation from discriminating chemical
  evidence;
- whether computational chemistry, simulation, cheminformatics, or AI-for-chemistry
  results are sensitive to model assumptions and independently validated;
- whether chemical-biology claims separate probe chemistry, target engagement,
  off-target effects, and biological readouts.

Typical revision direction: add orthogonal characterization, matched controls,
scope limits, uncertainty/replicate reporting, raw spectra or structures, calibrated
performance metrics, and clearer separation between observed chemistry and inferred
mechanism.

## Engineering

Use for manuscripts whose central contribution is an engineered system, device,
robot, platform, instrument, manufacturing process, autonomous lab, control method,
or algorithm embodied in a physical system.

Stress-test:

- whether design requirements are defined before performance is interpreted;
- whether validation is independent of training, calibration, optimization, screening,
  or design selection;
- whether baselines are current, tuned, fair, and evaluated under matched constraints;
- whether the operating envelope covers realistic loads, environments, duty cycles,
  latency, safety boundaries, batch variation, ageing, edge cases, and failure modes;
- whether simulations, digital twins, controllers, and surrogate objectives are
  calibrated against unseen physical evidence;
- whether autonomy, scalability, manufacturability, deployment, or translation claims
  exceed proof-of-concept evidence.

Typical revision direction: define the engineering task, add independent validation,
matched baselines, repeated batches or unseen tasks, uncertainty/failure reporting,
operating-envelope tests, and a narrower deployment or platform claim where needed.

## Materials Science

Use for manuscripts where claims depend on materials design, synthesis, processing,
composition, phase, microstructure, structure-property relations, device-material
performance, durability, scalability, or computational materials prediction.

Stress-test:

- whether material identity, composition, phase, purity, morphology, interfaces,
  defects, and spatial representativeness are established by convergent evidence;
- whether property and performance metrics are valid, normalized, and comparable
  under matched protocols;
- whether controls and benchmarks include closest prior, commercial, or state-of-the-art
  materials under equivalent tests;
- whether structure-property or degradation mechanisms are causal rather than only
  correlated;
- whether stability, cycling, ageing, humidity/thermal/chemical/mechanical stress,
  and post-test characterization support durability claims;
- whether manufacturability, processability, cost, toxicity, or application-readiness
  conclusions are supported at the same scale as the evidence.

Typical revision direction: add orthogonal composition/phase evidence, representative
characterization, matched benchmarks, uncertainty and batch variation, in situ/operando
or perturbation evidence for mechanisms, and realistic stability or process-window tests.

## Atmospheric Science

Use for manuscripts involving atmospheric dynamics, observations, reanalysis, satellite
products, aerosol-cloud-radiation interactions, atmospheric chemistry, extremes,
circulation mechanisms, attribution, or AI weather/climate models.

Stress-test:

- whether observations, reanalysis products, satellite retrievals, and model outputs
  measure the atmospheric variable claimed;
- whether scale, resolution, sampling, representativeness, and event selection support
  the stated spatial or temporal inference;
- whether trend, circulation, extreme-event, or attribution claims separate signal from
  internal variability, product uncertainty, model spread, and multiple testing;
- whether mechanism claims are supported by diagnostics that rule out plausible
  alternative circulation, forcing, transport, chemistry, or feedback explanations;
- whether AI weather/climate claims are evaluated out of sample and against physically
  meaningful baselines and metrics.

Typical revision direction: add product intercomparison, physical diagnostics, ensemble
or sensitivity tests, uncertainty propagation, scale-bounded wording, and clear
separation between detection, mechanism, and attribution.

## Climate Ecology

Use for manuscripts in ecology, biodiversity, conservation, forest/land-use science,
carbon or nitrogen cycling, ecosystem modelling, global change, or ecological management
implications.

Stress-test:

- whether biodiversity, community, ecosystem-function, trait, stability, or resilience
  claims use direct metrics rather than proxy variables alone;
- whether plots, sites, taxa, seasons, years, and sensors are representative of the
  generalization being made;
- whether ecological, climate, land-use, and management drivers are separable from
  confounders and site history;
- whether statistical models respect hierarchy, autocorrelation, multiple testing,
  detectability, and effect-size interpretation;
- whether carbon/nitrogen stocks, fluxes, sinks, emissions, and nutrient cycling are
  measured with appropriate units, baselines, and uncertainty;
- whether policy, conservation, restoration, or management implications are supported
  at the decision-relevant scale.

Typical revision direction: add sampling-frame justification, independent validation,
mechanism or driver-separation tests, uncertainty propagation, decision-scale caveats,
and narrower ecological or management claims where evidence is local.

## Hydrology

Use for manuscripts involving streamflow, runoff, groundwater, total water storage,
drought, flood, hydroclimate, water quality, water resources, hydrological remote
sensing, data assimilation, or hydrological modelling.

Stress-test:

- whether the hydrological variable supports the claim: stage is not discharge, total
  water storage is not groundwater, flood extent is not hazard, concentration is not
  load, and precipitation anomaly is not necessarily hydrological impact;
- whether water-balance closure, basin boundaries, storage terms, withdrawals,
  evapotranspiration, and human-water interactions are treated consistently;
- whether models are calibrated, validated, and tested against independent gauges,
  basins, periods, extremes, and process signatures;
- whether drought, flood, trend, attribution, or water-quality claims separate hazard,
  exposure, vulnerability, residence time, sampling frequency, and uncertainty;
- whether remote sensing or data-assimilation products are validated at the scale and
  temporal support of the inference.

Typical revision direction: define variables and basins precisely, add independent
gauge/product validation, close or explain the water budget, report uncertainty and
sensitivity, separate hazard from risk, and narrow regional or policy claims when needed.

## Remote Sensing and Earth Observation

Use for manuscripts centered on satellite products, retrieval algorithms, Earth-observation
maps, machine-learning classification/regression, spatial products, time series, or product
validation.

Stress-test:

- whether the remote-sensing product validly represents the physical, ecological, or
  social quantity inferred from it;
- whether validation data are independent, representative, and matched in spatial,
  temporal, and measurement support;
- whether spatial leakage, non-independent train/test splits, out-of-domain transfer,
  rare-event imbalance, and product intercomparison are handled;
- whether uncertainty from retrieval, classification, reference data, aggregation,
  temporal consistency, and sensor/product changes propagates into the headline claim;
- whether trend, decline, recovery, breakpoint, policy-period, or attribution claims
  separate temporal signal from seasonality, autocorrelation, disturbance, and product
  version changes;
- whether maps and inventories report accuracy, bias, false positives/negatives, and
  spatially explicit uncertainty.

Typical revision direction: add independent blocked validation, reference-data
uncertainty, product intercomparison, temporal-consistency checks, sensitivity to
aggregation and thresholds, and carefully bounded map, trend, or policy claims.
