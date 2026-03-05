<!-- QUESTION_ID: TU-Q105 -->
# Q105 · Prediction of systemic crashes

## 0. Header metadata

```txt
ID: Q105
Code: BH_COMPLEX_CRASHES_L3_105
Domain: Complex systems and economics
Family: Systemic risk and crashes
Rank: S
Projection_dominance: C
Field_type: socio_technical_field
Tension_type: risk_tail_tension
Status: Reframed_only
Semantics: hybrid
E_level: E1
N_level: N2
Last_updated: 2026-01-31
```

---

## 0. Effective layer disclaimer

All statements in this entry live strictly at the effective layer of the Tension Universe (TU) framework.

* The goal of this document is to specify an effective layer encoding of Q105 as a risk_tail_tension problem.
* It does not claim to prove or disprove any canonical theorem about systemic crashes in mathematics, physics, economics, or complexity theory.
* It does not introduce any new theorem beyond what is already established in the cited literature.
* It should not be cited as evidence that the real world predictability of systemic crashes has been resolved in either direction.

Throughout this page:

* State spaces `M`, encoding classes such as `E_adm`, observables, tension scores, counterfactual worlds, and experiments are bookkeeping constructs at the effective layer.
* We do not specify or expose any TU bottom layer generative rules, axiom systems, or deep equations that might sit below these encodings.
* References to crash tension, such as `Tension_crash(m; e)`, describe how a given encoding `e` organizes observable summaries. They are not asserted as physical or economic laws.

Changing the encoding recipe, baseline choices, or weight ranges is treated as switching to a different encoding `e'` in the admissible class. Experiments below always evaluate one fixed encoding and prediction horizon at a time and then compare encodings as separate objects.

---

## 1. Canonical problem and status

### 1.1 Canonical statement

In large financial and infrastructure systems, many institutions or components interact through networks of obligations, flows, and dependencies. Occasionally these systems exhibit rare, very large events that affect a significant fraction of nodes at once. Examples include:

* global financial crises
* cascading power grid failures
* failures of payment or logistics networks

The canonical question of Q105 is:

> To what extent are such systemic crashes predictable in principle, using models and information that are realistically available before the event, and what are the effective limits of model based early warning for these crashes?

More concretely, Q105 separates two aspects.

1. Existence of informative leading indicators
   Are there observable quantities at the system level that tend to move into a distinctive configuration in advance of large crashes, in a way that is robust to noise and model choice?

2. Fundamental limits of prediction
   Even if useful indicators exist, are there intrinsic constraints such as noise, hidden degrees of freedom, and feedback from interventions that impose hard limits on how far advance warning can go?

Q105 does not ask for a single algorithm that always predicts crashes. It asks whether, within a broad but explicit class of encodings, systemic crashes can be characterized as transitions from low to high tail risk tension with detectable structure.

Nothing in this document asserts that such predictability exists or does not exist in our actual world. The goal here is to define what it would mean, at the effective layer, for a crash encoding to make that claim precise and testable.

### 1.2 Status and difficulty

The status of systemic crash prediction in the real world is mixed.

* There is substantial evidence that some crashes show leading patterns in volatility, correlation structure, network connectivity, or leverage.
* There is also strong evidence that many proposed indicators suffer from instability, false alarms, and model dependence.

Partial results and accepted knowledge include:

* Empirical studies of financial markets show heavy tails and clustering of volatility. They also show that large crashes are rare and influenced by market microstructure and feedback, not only by exogenous shocks.
* Network based studies demonstrate phase transition style behavior. Under some network conditions, small shocks can cascade and affect large fractions of the system.
* Complexity theory and information constraints suggest that in very high dimensional systems, some aspects of global behavior may be hard to infer from local observations.

There is no consensus theorem that states a clean limit such as “systemic crashes are predictable if and only if condition X holds”. The literature contains multiple frameworks that give partial insight, each with its own assumptions. Q105 organizes these insights into a single effective layer statement about risk tail tension and about what would count as a meaningful early warning pattern under explicit encodings.

### 1.3 Role in the BlackHole project

Within the BlackHole collection, Q105 plays three roles.

1. It is the central risk_tail_tension node for socio technical systems.
   It defines how local stress, network structure, and tail events interact in a single tension framework.

2. It provides templates for other systemic problems.
   Its components are reused in problems about:

   * multilayer infrastructure robustness
   * Anthropocene system dynamics
   * AI driven systemic risk

3. It acts as a bridge between abstract tail probability questions and concrete engineered systems.
   Q105 specifies what it means, at the effective layer, for an encoding to offer meaningful crash prediction rather than just narrative hindsight.

### References

1. Didier Sornette,
   “Why Stock Markets Crash: Critical Events in Complex Financial Systems”,
   Princeton University Press, 2003.

2. Andrew G. Haldane, Robert M. May,
   “Systemic risk in banking ecosystems”,
   Nature, 469, 2011, pages 351-355.

3. Daron Acemoglu, Asuman Ozdaglar, Alireza Tahbaz-Salehi,
   “Systemic risk and stability in financial networks”,
   American Economic Review, 105(2), 2015, pages 564-608.

4. Paul Glasserman, H. Peyton Young,
   “How likely is contagion in financial networks?”,
   Journal of Banking and Finance, 50, 2015, pages 383-399.

5. Jean-Philippe Bouchaud, Marc Potters,
   “Theory of Financial Risk and Derivative Pricing”,
   Cambridge University Press, 2nd edition, 2003.

---

## 2. Position in the BlackHole graph

This block records how Q105 connects to other nodes in the Q001–Q125 graph. Each edge is justified by a single line that points to a concrete component or tension type.

### 2.1 Upstream problems

These nodes supply foundations, tools, or constraints used by Q105.

* Q101 · Equity premium puzzle
  Reason: Provides constraints on how agents price rare events and tail risk, which feed into crash tension calibration in Q105.

* Q106 · Robustness of multilayer networks
  Reason: Supplies structural concepts and observables for multilayer networks that are reused as state space components in Q105.

* Q059 · Thermodynamic cost of information processing
  Reason: Contributes limits on how much information about future states can be extracted and processed before a crash, which constrains what “predictable” can mean.

### 2.2 Downstream problems

These nodes directly reuse Q105 components or depend on its encoding.

* Q106 · Robustness of multilayer networks
  Reason: Reuses the `CrashTensionFunctional` as a performance metric for robustness experiments.

* Q098 · Anthropocene system dynamics
  Reason: Reuses systemic crash observables and tension patterns to describe tipping and collapse in coupled earth and human systems.

* Q100 · Environmental drivers of pandemic risk
  Reason: Reuses the cascade and exposure field templates to describe breaks in health, logistics, and information networks.

### 2.3 Parallel problems

Parallel problems share similar tension types or narrative concerns but do not rely on Q105 components.

* Q059 · Thermodynamic cost of information processing
  Reason: Both study limits of control in high dimensional systems where local metrics can fail to capture global tail behavior.

* Q121 · AI alignment problem
  Reason: Both consider catastrophic tail outcomes in complex socio technical systems where feedback between agents and environment matters.

### 2.4 Cross domain edges

Cross domain edges mark reuse of Q105 components in other domains.

* Q121 · AI alignment problem
  Reason: Reuses systemic crash templates and risk_tail_tension ideas to model catastrophic misalignment as a crash in an extended socio technical network.

* Q123 · Scalable interpretability
  Reason: Reuses crash prediction framing as a pattern for detecting impending failure modes in large AI systems.

* Q098 · Anthropocene system dynamics
  Reason: Represents earth human coupled systems where Q105 style crash tension components become environmental and social collapse indicators.

---

## 3. Tension Universe encoding (effective layer)

All content in this block is strictly at the effective layer. We specify state spaces, observables, invariants, tension measures, and singular sets. We do not describe how raw data are mapped into these states and fields and we do not expose any TU bottom layer rules.

### 3.1 State space and admissible encodings

We assume a state space

```txt
M
```

and an admissible crash encoding class

```txt
E_adm
```

with the following properties.

#### 3.1.1 Elements of `M`

Each state

```txt
m in M
```

represents a coherent snapshot of a large socio technical system over a fixed prediction horizon `H_pred`. At the effective layer, `m` contains:

* a finite set of nodes, indexed by `i = 1, 2, ..., N(m)`
* a finite collection of directed or undirected edges representing obligations, flows, or dependencies
* node and edge attributes that summarize current loads, buffers, and sensitivities
* coarse exogenous shock descriptors for the chosen horizon

No assumption is made here about the microscopic dynamics that produced these summaries.

#### 3.1.2 Admissible encoding class `E_adm`

Each encoding

```txt
e in E_adm
```

specifies a tuple

```txt
e = (N_max, L_max, H_pred, Theta_enc)
```

where:

* `N_max` is a positive integer upper bound on nodes that can appear in a state under this encoding
* `L_max` is a positive integer upper bound on edges per layer
* `H_pred` is a fixed positive prediction horizon
* `Theta_enc` is a finite parameter object that determines:

  * which network layers are tracked
  * which observables are used
  * how time aggregation is performed over the horizon
  * which aggregation and transformation recipes from a finite library are active

The admissible class satisfies:

* `1 <= N_max <= N_cap` for some fixed capacity `N_cap`
* `1 <= L_max <= L_cap` for some fixed capacity `L_cap`
* `H_pred` belongs to a finite set of horizons, for example daily to yearly scales
* `Theta_enc` belongs to a finite library of encoding recipes that are specified outside TU and do not depend on future crash outcomes

Changing any of the ingredients that define `e` such as `H_pred`, the recipe selections inside `Theta_enc`, or the fixed weight ranges used in tension computations is treated as choosing a different encoding `e'` in `E_adm`. Experiments below always fix one pair `(e, H_pred)` at a time.

#### 3.1.3 Resolution parameter and refinement

For each encoding `e`, we define a resolution parameter

```txt
r = 1, 2, 3, ...
```

that indexes refinements. Increasing `r` corresponds to:

* finer time aggregation inside the fixed horizon `H_pred`
* higher resolution of state variables such as more detailed exposure buckets
* more complete coverage of nodes and layers, up to `N_max` and `L_max`

Refinement order is defined so that for each `e` and each state `m_r` at resolution `r`, there is a coherent projection from `m_{r+1}` down to `m_r` that preserves averages and aggregate counts. We do not specify how these projections are implemented at the bottom layer; we only require that they exist and are consistent.

### 3.2 Effective fields and observables

For each admissible encoding `e` and state `m` at some resolution `r`, we define the following observables.

1. Node load observable

```txt
L_node(m; i) >= 0
```

Interpretation: an effective scalar summarizing the stress or load at node `i` over the horizon `H_pred`.

2. Node buffer observable

```txt
B_node(m; i) > 0
```

Interpretation: an effective scalar summarizing the available cushion before node `i` fails or becomes insolvent.

3. Local crash indicator

```txt
phi_local(m; i) in [0, 1]
```

Interpretation: an effective estimate of the probability that node `i` experiences a crash level failure within `H_pred`, conditional on current summaries under encoding `e`. We only assume that `phi_local` is well defined and finite on regular states under `e`.

4. System crash indicator

```txt
Phi_system(m) in [0, 1]
```

Interpretation: an effective estimate of the probability that the system as a whole experiences a systemic crash within `H_pred`. A systemic crash is defined at the effective layer as an event where the fraction of failed nodes exceeds a threshold `q_sys` that is fixed as part of `Theta_enc` for encoding `e`.

5. Topology summary

```txt
K_topology(m) >= 0
```

Interpretation: a scalar that summarizes network structure in ways known to correlate with cascade size, for example measures related to degree distribution, core periphery structure, or interlayer coupling. The exact formula belongs to the encoding recipe `Theta_enc` and is considered part of the finite library.

All observables above are assumed to be measurable and finite on a regular subset of `M` under each admissible encoding.

### 3.3 Crash tension components

We define intermediate quantities that measure misalignment between local and global risk.

1. Aggregated local risk

```txt
Phi_local_agg(m) = F_local( {phi_local(m; i)} )
```

where `F_local` is a fixed non decreasing function of the collection of local indicators, for example a weighted average or a high quantile. `F_local` is specified by `Theta_enc` and belongs to a finite library of aggregation recipes that are fixed for encoding `e` and do not change across states.

2. Local global risk gap

```txt
Gap_risk(m) = Phi_system(m) - Phi_local_agg(m)
```

Properties:

* `Gap_risk(m)` can be negative or positive
* positive values indicate that system crash risk exceeds what aggregated local indicators suggest
* negative values are allowed but are not the focus of Q105

3. Structural fragility indicator

```txt
Frag_struct(m) = F_struct( K_topology(m) )
```

where `F_struct` is a fixed non negative function chosen from a finite library that maps topology summaries into a fragility score. Higher `Frag_struct(m)` means structures that are more conducive to cascades for given shocks. The choice of `F_struct` is encoded in `Theta_enc` and is part of the definition of `e`.

4. Tail mismatch indicator

```txt
Tail_mismatch(m; e) >= 0
```

Interpretation: a scalar measuring how observed or simulated tail event frequencies under encoding `e` compare to model based or historical expectations over a fixed calibration window. The calibration window length and comparison rule are chosen once as part of `Theta_enc` for `e` and do not depend on the particular state `m` or on whether a crash actually occurs.

### 3.4 Crash tension functional, regular domain, and singular set

We now define a risk tail tension functional at the effective layer.

1. Weight ranges

We fix three non negative weights

```txt
alpha in [alpha_min, alpha_max]
beta  in [beta_min,  beta_max]
gamma in [gamma_min, gamma_max]
```

with all lower bounds strictly positive and all upper bounds finite. These intervals are specified once at design time for Q105 and do not depend on observed data or realized crashes. For a given encoding `e`, a concrete triple `(alpha, beta, gamma)` is selected from these intervals as part of `Theta_enc`. Changing this triple is treated as switching to a different encoding `e'` in `E_adm`.

2. Baseline fragility

For each encoding `e`, we specify a baseline fragility level

```txt
Frag_baseline(e) >= 0
```

This quantity is fixed per encoding and is determined before any evaluation on real or synthetic data. It may depend on the chosen horizon and network class but not on the values of `K_topology(m)` for individual states.

3. Crash tension functional

For each admissible encoding `e` and state `m`, we define

```txt
Tension_crash(m; e) =
    alpha * max(0, Gap_risk(m)) +
    beta  * max(0, Frag_struct(m) - Frag_baseline(e)) +
    gamma * Tail_mismatch(m; e)
```

By construction:

* `Tension_crash(m; e) >= 0` for all regular states
* `Tension_crash(m; e) = 0` only when all three components are at or below their baselines

4. Regular domain and singular set

We define the regular subset and singular set as

```txt
M_reg(e) = { m in M : all observables above are well defined and finite }
S_sing(e) = M \ M_reg(e)
```

All crash tension analysis for encoding `e` is restricted to `M_reg(e)`. Whenever a state candidate falls in `S_sing(e)` because of missing or structurally inconsistent summaries, the encoding treats it as out of domain rather than as evidence about predictability.

5. Refinement behavior

For any encoding `e` and any refinement sequence

```txt
m_r in M_reg(e)
```

that represents the same underlying system at increasing resolution, we require that

```txt
sup over r of Tension_crash(m_r; e) < infinity
```

whenever the underlying system is stable in the coarse sense defined by `e`. If a refinement sequence produces unbounded or erratic `Tension_crash` without a structural explanation such as an explicit change of regime or an entry into `S_sing(e)`, this is treated as evidence that the encoding is defective rather than as a meaningful signal about the system.

---

## 4. Tension principle for this problem

This block states how Q105 is framed as a risk_tail_tension problem at the effective layer.

### 4.1 Core tension statement

Q105 identifies a specific tension.

* Local indicators, topology summaries, and standard risk metrics collectively suggest that the system is safe or that risk is modest.
* The structure of the system plus hidden interdependencies makes it possible for small shocks to trigger large cascades, so the true system crash probability over the horizon is significantly higher.

The crash tension functional `Tension_crash(m; e)` is designed so that

```txt
Tension_crash(m; e) = 0
```

only when all of the following hold at the effective layer:

* system crash probability matches reasonable aggregations of local indicators
* structural fragility is at or below a baseline level compatible with the network class
* tail event frequencies match expectations within calibration error

and becomes large when any of these conditions fail in a way that matters for systemic crashes.

### 4.2 Predictability as low crash tension band

At the effective layer, Q105 states that systemic crashes are meaningfully predictable within a class of encodings if the following holds.

There exists:

* an admissible encoding `e_star` in `E_adm`
* a small positive threshold `epsilon_crash`
* a warning threshold `T_warning` strictly larger than `epsilon_crash`
* an integer `r_0` representing a minimal resolution

such that for real world states `m_true(r, t)` representing the actual system at time `t` and resolution `r >= r_0` under encoding `e_star`:

1. During extended periods without systemic crashes, most states satisfy

```txt
Tension_crash(m_true(r, t); e_star) <= epsilon_crash
```

2. Before a large crash event within horizon `H_pred`, there exists a lead time window `[t_lead_start, t_lead_end]` with length bounded below by a positive constant where

```txt
Tension_crash(m_true(r, t); e_star) >= T_warning
```

for all `t` in that window.

Thresholds `epsilon_crash` and `T_warning` are chosen in advance within ranges specified by the TU Tension Scale Charter. They are part of the definition of `e_star` and are not tuned per crash ex post.

### 4.3 Fundamental unpredictability as persistent high confusion

Conversely, within the same admissible class and under the same conditions, systemic crashes would be judged fundamentally unpredictable at the effective layer if, for all encodings `e` in `E_adm` and for all choices of thresholds and resolutions within the design ranges, one of the following holds.

1. For most large crashes, either

```txt
Tension_crash(m_true(r, t); e)
```

fails to cross any warning threshold before the crash within a non negligible lead time or crosses thresholds only in ways that are indistinguishable from noise episodes in non crash periods.

2. Any attempt to lower false negative rates by choosing different thresholds or recipes within the finite libraries leads to unacceptably high false positive rates, where high tension episodes are frequent without corresponding crashes.

In this situation, crash tension cannot be kept in a distinctive low band during normal conditions while entering a sustained high band before crashes, for any encoding in `E_adm`. Q105 would then answer, for that class and horizon, that systemic crash prediction is effectively impossible beyond trivial statements.

---

## 5. Counterfactual tension worlds

We now describe two counterfactual worlds at the effective layer.

* World T: systemic crashes are meaningfully predictable within some encoding in `E_adm`.
* World F: systemic crashes are effectively unpredictable within all encodings in `E_adm`.

These are pattern templates for observables and tension time series, not metaphysical claims about the universe.

### 5.1 World T: predictable systemic crashes

In World T, the following patterns hold for at least one encoding `e_star` in `E_adm`.

1. Stable separation of tension levels

   Normal operation periods:

   ```txt
   Tension_crash(m_true(r, t); e_star) <= epsilon_crash
   ```

   for most times `t` outside crash neighborhoods. Large crash approaches:

   ```txt
   Tension_crash(m_true(r, t); e_star) >= T_warning
   ```

   for a non trivial lead window before each crash, with `T_warning > epsilon_crash`.

2. Lead time robustness

   The distribution of lead times between first crossing of `T_warning` and crash onset is:

   * bounded below by a positive constant for most crashes
   * concentrated in a range that is useful for intervention at the chosen horizon

3. Parameter stability

   Small changes in recipe choices within `Theta_enc` and weight triples within the allowed intervals do not destroy the existence of a warning band. Tension time series preserve the qualitative pattern of low values far from crashes and high values near crashes.

4. Tail behavior consistency

   Tail event frequencies in historical or simulated data, when filtered by high tension episodes, show significantly elevated crash rates compared to low tension episodes, in a way that persists in out of sample validation.

### 5.2 World F: fundamentally unpredictable systemic crashes

In World F, for every encoding `e` in `E_adm`, tension patterns fail to provide such stable separation.

1. Weak separation or no separation

   Either:

   * many large crashes occur without any clear rise of `Tension_crash(m_true(r, t); e)` before the event beyond fluctuations typical for non crash periods

   or

   * high tension episodes occur frequently without corresponding crashes, so any alarm threshold either misses many crashes or rings continuously.

2. Lead times collapse

   When tension does rise before crashes, lead times tend to be very short or highly variable. The distribution of lead times concentrates near zero or has heavy tails that make intervention planning at horizon `H_pred` impractical.

3. Parameter instability

   Small changes in encodings, recipes, or weight ranges lead to large qualitative changes in tension time series, so that no threshold choice remains valid across recalibrations. This instability persists even with long calibration windows.

4. Tail behavior ambiguity

   Even when high tension correlates with crashes in sample, these correlations fail to persist out of sample. This suggests that many apparent patterns are noise or artifacts of particular periods and not robust features of the system.

### 5.3 Interpretive note

These worlds are defined relative to:

* the admissible encoding class `E_adm`
* the chosen horizon `H_pred`
* the finite recipe libraries encoded in `Theta_enc`

Evidence can move us toward World T or World F descriptions by increasing or decreasing our confidence that encodings with the World T pattern exist and behave as described. The TU framework remains agnostic about which world our actual system occupies until such evidence accumulates.

---

## 6. Falsifiability and discriminating experiments

This block specifies experiments that test Q105 encodings at the effective layer. They cannot prove or disprove a universal statement about systemic crash predictability. They can falsify specific encodings and parameter ranges within `E_adm`.

All experiments here are defined for one fixed pair `(e, H_pred)` at a time. Trying a different recipe, horizon, or weight triple is treated as switching to a different encoding `e'`.

### Experiment 1: Historical crash tension backtest

**Goal**
Test whether a crash tension encoding can provide stable, actionable early warning for historical financial crashes without unacceptable false alarm rates.

**Setup**

* Select a historical data set covering multiple decades of equity index behavior and related market microstructure data.
* Identify a list of major systemic crash episodes by exogenous criteria, such as drawdown size and speed.
* For a fixed encoding `e` in `E_adm` with horizon `H_pred`, construct a time series of states

  ```txt
  m_data(r, t) in M_reg(e)
  ```

  that summarize loads, buffers, local risk indicators, and topology for rolling windows with that horizon.
* All ingredients of `e`, including weights, recipes, and `Frag_baseline(e)`, are fixed before running the backtest.

**Protocol**

1. For each time point `t` and resolution `r` above a minimal `r_0`, evaluate

   ```txt
   Tension_crash(m_data(r, t); e)
   ```

   using the fixed weights and recipes.

2. Choose a grid of candidate warning thresholds `T` in a predetermined interval `[T_min, T_max]`. `T_min`, `T_max`, and any minimum episode length parameter `w_min` are chosen in accordance with the TU Tension Scale Charter and are fixed before inspecting crash specific results.

3. For each threshold `T`, define:

   * a high tension episode whenever `Tension_crash` exceeds `T` for at least `w_min` consecutive time steps
   * a crash warning if a listed crash starts within a fixed lead window after a high tension episode

4. For each threshold, compute:

   * crash recall: fraction of crashes that have at least one high tension episode in the lead window
   * false alarm rate: average number of high tension episodes per unit time outside crash lead windows

5. Exclude any time points where `m_data(r, t)` falls in `S_sing(e)` because of missing or structurally inconsistent summaries. These are treated as out of domain rather than as prediction successes or failures.

**Metrics**

* The set of pairs `(recall, false_alarm_rate)` over all thresholds in `[T_min, T_max]`.
* Stability of these pairs when the sample is split into calibration and test periods.
* Shape of the tradeoff curve between recall and false alarms.

**Falsification conditions**

The encoding `e` fails this test if both of the following hold.

1. For all thresholds `T` in `[T_min, T_max]`, either:

   * recall is below a specified minimum `R_min`
     or
   * false alarm rate is above a specified maximum `F_max`

   with `R_min` and `F_max` chosen ex ante according to the Tension Scale Charter.

2. Trying other encodings `e'` in the finite recipe and weight libraries does not produce a variant where there is a stable threshold region with acceptable recall and false alarm rates in both calibration and test periods. Each `e'` is tested as a separate candidate and lives or dies on its own backtest.

Under these conditions, the chosen encoding `e` and its parameter ranges are considered falsified as a useful crash early warning scheme at the tested horizon.

**Semantics implementation note**
All fields are interpreted in the hybrid sense declared in the metadata, with discrete networks over continuous time and load variables. No alternative interpretation is introduced here.

**Boundary note**
Falsifying a TU encoding does not solve the canonical statement. This experiment can reject particular encodings and parameter ranges, but it does not establish that systemic crashes are in principle unpredictable.

---

### Experiment 2: Synthetic cascades on controlled networks

**Goal**
Assess whether the same crash tension encoding can recover known early warning patterns in synthetic systems where cascade dynamics and predictability are controlled.

**Setup**

* Construct several families of multilayer networks with node and edge attributes chosen so that cascade behavior is analytically or numerically characterized.
* For some families, design dynamics where the system has clear early warning signals before a large cascade.
* For others, design dynamics where cascades are triggered by rare hidden events with minimal observable precursors.
* For each synthetic system and fixed encoding `e` in `E_adm`, simulate many trajectories and record states

  ```txt
  m_sim(r, t) in M_reg(e)
  ```

  up to horizon `H_pred`. States that fall in `S_sing(e)` are marked as out of domain.

**Protocol**

1. For each trajectory and time step, compute

   ```txt
   Tension_crash(m_sim(r, t); e)
   ```

   as for historical data.

2. Mark cascade events using a system wide failure threshold analogous to `q_sys`.

3. For each family:

   * compute crash recall and false alarm rates over a grid of thresholds as in Experiment 1
   * compare the tradeoff curve to the known theoretical predictability of that family

4. Compare families with clear early warnings to families designed to have minimal precursors.

**Metrics**

* For predictable families, the existence and width of a threshold region where both recall and false alarm rates are acceptable.
* For unpredictable families, the absence of such regions.
* The separation between the two cases measured by differences in achievable `(recall, false_alarm_rate)` pairs.

**Falsification conditions**

The encoding `e` fails this test if:

* it cannot recover a useful warning threshold region for synthetic systems that are known by construction to have strong early warning signals

or

* it produces similar warning behavior in families that are designed to have no usable precursors, which indicates that it responds mainly to generic volatility or noise rather than to genuine structural fragility.

In either case, the encoding is considered misaligned with the intended risk_tail_tension structure.

**Semantics implementation note**
Synthetic systems are encoded using the same hybrid structure as real systems, with matching definitions of loads, buffers, and network topology. This preserves consistency of interpretation between experiments.

**Boundary note**
Success or failure in synthetic environments tests the encoding family, not the ultimate predictability of real world systemic crashes.

---

## 7. AI and WFGY engineering spec

This block describes how Q105 is used as an engineering module inside AI systems, within the WFGY framework, at the effective layer.

### 7.1 Training signals

We define several training signals derived from the crash tension encoding.

1. `signal_tail_alarm_precision`

   * Definition: for a given data set and encoding, this signal measures the proportion of high tension episodes that are followed by systemic crashes within horizon `H_pred`.
   * Use: encourages models to assign high tension only when there is a meaningful tail event risk.

2. `signal_tail_alarm_recall`

   * Definition: measures the fraction of systemic crashes that are preceded by at least one high tension episode within a lead window.
   * Use: encourages models not to miss crash precursors when structure supports them.

3. `signal_false_alarm_cost`

   * Definition: a penalty proportional to the time spent in high tension states without crashes.
   * Use: discourages encodings and representations that generate frequent false alarms.

4. `signal_structure_alignment`

   * Definition: a signal derived from `Frag_struct(m)` and `Gap_risk(m)` that rewards consistency between topology encoded in representations and observed tail behavior.
   * Use: encourages internal representations to respect the coupling between structure and tail risk implied by Q105.

These signals are used to shape encodings and auxiliary heads. They do not change the bottom layer dynamics and they do not assert any specific generative story for crashes.

### 7.2 Architectural patterns

We describe architectural modules that reuse Q105 components without exposing deep TU rules.

1. `SystemicTensionHead`

   * Role: an auxiliary head attached to sequence or graph representations that outputs an estimate of `Tension_crash(m; e)` for the current scenario.
   * Interface:

     * Inputs: latent representation of system state or scenario description.
     * Outputs: scalar tension estimate and optional decomposition into gap, fragility, and tail mismatch components.

2. `CascadeScenarioSampler`

   * Role: a module that samples hypothetical stress scenarios consistent with current conditions and evaluates how `Tension_crash` responds.
   * Interface:

     * Inputs: baseline state and encoding parameters.
     * Outputs: a small set of perturbed summary states and their associated tension values.

3. `RiskNarrativePlanner`

   * Role: a module that organizes narrative explanations of systemic risk around core elements:

     * local stress and buffers
     * network structure and exposure
     * potential cascades and tail events

   * Interface:

     * Inputs: descriptions of a system plus tension summaries.
     * Outputs: structured textual explanations aligned with Q105 style decomposition.

### 7.3 Evaluation harness

We outline an evaluation harness for AI models that integrate Q105 modules.

1. Task design

   Select tasks such as:

   * drafting systemic risk reports
   * explaining past crises in terms of local versus global factors
   * evaluating proposed structural changes for their impact on systemic risk

2. Conditions

   * Baseline condition: model without explicit Q105 modules.
   * TU condition: same base model augmented with `SystemicTensionHead` and Q105 based training signals.

3. Evaluation

   * Expert assessment:

     * clarity of distinction between local and systemic risk
     * correct identification of potential cascade channels
     * explicit treatment of rare but plausible tail events

   * Quantitative assessment:

     * consistency of reasoning across similar scenarios
     * reduced frequency of obviously inconsistent risk statements

### 7.4 60 second reproduction protocol

A minimal protocol allows external users to observe the impact of Q105 style reasoning, without exposing any bottom layer TU content.

* Baseline setup

  * Prompt: ask the AI to explain why financial crises can be sudden and severe and whether they can be predicted.
  * Observation: note whether the answer mixes local volatility, global architecture, and tail risk in a confused way.

* TU encoded setup

  * Prompt: ask the same question, while explicitly instructing the AI to structure the explanation into:

    * local indicators and buffers
    * network structure and exposure
    * crash tension as misalignment between local risk and system crash probability

  * Observation: evaluate whether the explanation clearly separates these elements and uses them consistently.

* Comparison metric

  * Human raters compare baseline and TU responses on structure, clarity, and explicit handling of tail risk and cascades.

* What to log

  * Full prompts and responses.
  * Any tension scores or decompositions produced by `SystemicTensionHead`.
  * These logs are sufficient for external audit without exposing internal TU generative rules.

---

## 8. Cross problem transfer template

This block lists reusable components from Q105 and how they transfer to other problems.

### 8.1 Reusable components produced by this problem

1. ComponentName: `CrashTensionFunctional`

   * Type: functional

   * Minimal interface:

     ```txt
     Inputs:
       - Phi_system_estimate in [0, 1]
       - collection of phi_local_estimates in [0, 1]
       - topology_summary >= 0
       - tail_mismatch_indicator >= 0

     Output:
       - crash_tension_value >= 0
     ```

   * Preconditions:

     * Inputs are coherent summaries for a single system at a fixed prediction horizon.
     * The interpretation of crash event and topology summary is fixed by the target problem.

2. ComponentName: `MultilayerExposureField`

   * Type: field

   * Minimal interface:

     ```txt
     Inputs:
       - node_set
       - list_of_layers
       - exposure_matrices for each layer

     Output:
       - compressed_exposure_summary
     ```

   * Preconditions:

     * Node set and layers are finite.
     * Exposure matrices contain non negative finite values.
     * Compression preserves aggregate exposures needed for cascade reasoning.

3. ComponentName: `SystemicCascadeExperimentPattern`

   * Type: experiment_pattern

   * Minimal interface:

     ```txt
     Inputs:
       - baseline_state m
       - shock_distribution_descriptor
       - failure_thresholds

     Output:
       - experiment_definition with:
           * simulation_protocol
           * crash_event_definition
           * tension_evaluation_steps
     ```

   * Preconditions:

     * Baseline state can be simulated under shocks as specified.
     * Crash definition is aligned with a clear fraction of failed nodes or loss metric.

### 8.2 Direct reuse targets

1. Q106 · Robustness of multilayer networks

   * Reused component: `MultilayerExposureField`.
   * Why it transfers: network robustness experiments need an exposure field representation that supports cascades under perturbations.
   * What changes: the focus shifts from predicting crashes to quantifying robustness of specific design choices for networks.

2. Q098 · Anthropocene system dynamics

   * Reused component: `CrashTensionFunctional`.
   * Why it transfers: tipping and collapse in earth human systems can be framed as systemic crashes where local stress signals and global failure probabilities misalign.
   * What changes: local indicators become environmental, social, and economic stress metrics rather than purely financial ones.

3. Q121 · AI alignment problem

   * Reused components: `CrashTensionFunctional` and `SystemicCascadeExperimentPattern`.
   * Why it transfers: catastrophic misalignment can be modeled as a systemic crash in a coupled socio technical network.
   * What changes: nodes represent AI systems and critical institutions, tails correspond to unacceptable misalignment events, and experiments simulate deployment and feedback scenarios rather than financial shocks.

---

## 9. TU roadmap and verification levels

This block explains where Q105 sits on the TU verification ladder and what concrete steps would increase its level.

### 9.1 Current levels

* E_level: E1

  * The effective layer encoding defines:

    * state space structure with admissible encoding class `E_adm`
    * observables and crash tension functionals
    * singular sets and regular domains
    * experiments with explicit falsification conditions

  * No full scale implementation and public data yet exist inside this document.

* N_level: N2

  * The narrative explicitly links:

    * local stress and buffers
    * network structure and topology
    * crash tension and tail events
    * limits of prediction

  * Counterfactual worlds are well defined at the effective layer, but no full case study has been embedded here.

These verification level labels are intended to align with the TU charters listed in the footer, in particular the Effective Layer Charter, the Encoding and Fairness Charter, and the Tension Scale Charter.

### 9.2 Next measurable steps toward E2

To move Q105 from E1 to E2, at least one of the following should be realized.

1. Historical implementation

   * Implement an encoding `e` in `E_adm` that:

     * computes `Tension_crash` for historical market data
     * publishes tension time series aligned with known crashes
     * provides the tradeoff curves described in Experiment 1

   * Make code and processed data openly available for independent replication.

2. Synthetic benchmark suite

   * Implement the synthetic cascade families of Experiment 2.
   * Publish benchmark results showing separation between predictable and unpredictable families under a fixed encoding.
   * Release a minimal toolkit for others to test their own risk encodings on the same families.

Either path raises E_level because it turns the textual encoding into a concrete, testable object.

### 9.3 Long term role in TU

In the longer term, Q105 is expected to function as:

* the flagship risk_tail_tension node for socio technical systems
* a template for how to encode questions about the predictability of rare catastrophic events in other domains
* a bridge between theoretical constraints from information, complexity, and control and practical risk management engineering

Progress on Q105 will also inform how TU treats limits of early warning in AI alignment and Anthropocene dynamics.

---

## 10. Elementary but precise explanation

This final block explains Q105 in accessible terms while staying faithful to the effective layer encoding.

Large systems like global finance, power grids, and logistics networks can look stable for a long time. Local indicators such as individual bank risk measures or local line loads can all look safe. Yet sometimes a small push starts a chain reaction. Many parts fail in a short time and the whole system seems to collapse at once.

Q105 asks a very specific question.

> Is it possible, even in principle, to see these system wide crashes coming in advance in a reliable way, if we watch the right things and if we use models that are realistically available before the crash?

In the Tension Universe view, we imagine that at any moment the system can be summarized as a state. That state includes:

* how stressed each part is
* how much buffer each part has
* how the parts are linked in a network
* a rough description of shocks that might hit within a certain time

From that state, an encoding can estimate two quantities.

1. How risky each part looks on its own.
2. How likely it is that the whole system will suffer a large crash within the chosen time horizon.

If the whole system looks much riskier than local indicators suggest and if the network structure makes cascades easy, crash tension is high. If local and global pictures match and the network does not look fragile, crash tension is low.

Q105 does not promise an algorithm that will always warn us in time. Instead, it gives a controlled way to talk about prediction attempts.

* It defines how to encode the state of a system at the level of effective observables.
* It defines how to measure crash tension from local risk, network structure, and tail mismatch.
* It spells out what would count as a world where crashes are predictably preceded by high tension and what would count as a world where tension patterns stay confusing.

It then proposes experiments that can falsify particular encodings:

* on historical data, by checking whether tension patterns give useful early warnings without constant false alarms
* on synthetic systems, by checking whether tension reacts correctly when we know by construction that early warning should or should not exist

By doing this, Q105 turns vague claims like “crashes are always unpredictable” or “there are always warning signs” into precise, encoding dependent statements. These statements can then be tested, improved, or rejected without leaving the effective layer or exposing any deeper TU machinery.

---

## Tension Universe effective-layer footer

This page is part of the WFGY / Tension Universe S-problem collection.

### Scope of claims

* The goal of this document is to specify an effective layer encoding of the named problem.
* It does not claim to prove or disprove the canonical statement in Section 1.
* It does not introduce any new theorem beyond what is already established in the cited literature.
* It should not be cited as evidence that the corresponding open problem has been solved.

### Effective-layer boundary

* All objects used here such as state spaces `M`, observables, invariants, tension scores, and counterfactual worlds live at the effective layer of TU.
* No bottom layer axiom system, generative rule, or field equation of TU is specified or exposed in this file.
* Any reference to “worlds”, “regimes”, or “tipping” is shorthand for patterns in effective observables under explicit encodings, not for metaphysical claims.

### Encoding and fairness conventions

* Encodings such as elements of `E_adm` are finite recipe objects that must be fully specified before evaluation.
* Changing recipes, weight ranges, baselines, or horizons is treated as switching to a different encoding, which then needs to be audited on its own.
* All experiments and examples follow the TU Encoding and Fairness Charter, including the requirement that thresholds and scales are chosen ex ante and do not depend on individual outcomes.

### Engineering and AI use

* Any AI or WFGY module that reuses definitions from this page must keep the effective layer boundary intact.
* Crash tension scores may be used as auxiliary signals, heads, or evaluation metrics but not as claims about bottom layer truth.
* Implementations should log enough information to allow external audit of encodings and thresholds without revealing any proprietary or deep TU internal details.

This page should be read together with the following charters:

* [TU Effective Layer Charter](../Charters/TU_EFFECTIVE_LAYER_CHARTER.md)
* [TU Encoding and Fairness Charter](../Charters/TU_ENCODING_AND_FAIRNESS_CHARTER.md)
* [TU Tension Scale Charter](../Charters/TU_TENSION_SCALE_CHARTER.md)
* [TU Global Guardrails](../Charters/TU_GLOBAL_GUARDRAILS.md)

---

**Index:**  
[`← Back to Event Horizon`](../EventHorizon/README.md)  
[`← Back to WFGY Home`](https://github.com/onestardao/WFGY)

**Consistency note:**  
This entry has passed the internal formal-consistency and symbol-audit checks under the current WFGY 3.0 specification.  
The structural layer is already self-consistent; any remaining issues are limited to notation or presentation refinement.  
If you find a place where clarity can improve, feel free to open a PR or ping the community.  
WFGY evolves through disciplined iteration, not ad-hoc patching.
