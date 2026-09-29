# Model assumptions

Status: not selected. Record each neural, sensory, and motor assumption here after checking the relevant primary source Methods. Keep anatomical observations separate from modeled behavior.

| Assumption | Evidence or rationale | Limitation | Protocol version |
| --- | --- | --- | --- |

## E04 source extraction — candidate only (2026-09-25)

The author repository for Shiu et al. is evidence about that implementation, not a decision to adopt it. Its README says the paper used FlyWire v630; the repository provides an alternative v783 input configuration (FW-018). The published article's Methods were subsequently opened via PubMed Central (FW-025–FW-027). The repository revision has not been pinned, and no v783 reproduction has been attempted.

| Item | Source-coded value or behavior | Exact evidence | Project status |
| --- | --- | --- | --- |
| Simulator | Python with Brian2 | FW-018; README “Brian 2 performance” | Candidate only |
| Neural state | `dv/dt = (v_0 - v + g)/t_mbr`; `dg/dt = -g/tau` | FW-019; `model.py`, `default_params['eqs']`; FW-025, Methods equations | Published model; candidate only |
| Spike/reset | Spike when `v > v_th`; paper describes resetting potential and synaptic state with refractory period; code reset string includes `v = v_rst`, `w = 0`, `g = 0*mV` | FW-019, `model.py`; FW-025, Methods “Computational model” | Candidate only; inspect code/reset semantics before porting |
| Synapse | Brian2 `on_pre='g += w'` with fixed delay; assigned from prepared `Excitatory x Connectivity` column times `w_syn` | FW-019–FW-020; `model.py`, `create_model` | Input sign/weight derivation and mapping to any v783 product UNVERIFIED |
| Input and silence | README describes fixed-frequency Poisson activation and zeroing synaptic connections for silencing | FW-020; README “Usage” | Candidate only; vehicle sensor mapping UNVERIFIED |
| Outputs | README describes spike times and rates of affected neurons | FW-020; README “Usage” | Left/right motor decoding UNVERIFIED |
| Dataset | Published implementation v630; README supplies v783 filenames/config | FW-018; README “Version 783” | Do not mix IDs or prepared data with selected v783 lineage |

No value in this table is a frozen FlyAI parameter. The simulator time step, signs, source-to-product conversion, sensor encoding, and motor mapping require an explicit, versioned choice before P4.

### Published parameter and sign record (FW-025–FW-027)

| Parameter or rule | Published value/rule | Location and limit |
| --- | --- | --- |
| Rest and reset potential; threshold | −52 mV; −52 mV; −45 mV | Methods “Computational model”; v630 setup |
| Membrane resistance and capacitance | 10 kΩ cm²; 2 µF cm⁻², giving a 20 ms membrane time constant | Same Methods section; time constant follows from the stated product |
| Refractory, synaptic decay, delay | 2.2 ms; 5 ms; 1.8 ms | Same Methods section |
| Per-synapse `W_syn` | 0.275 mV | Same Methods section; paper calls this a free parameter calibrated on sugar-GRN/MN9 response, so direct reuse in a different task is a new choice |
| Connection increment | Synapse count × presynaptic sign (+1/−1) × `W_syn`; `g_i` increments after a presynaptic spike | Same Methods section; count is a proxy for physiological effect |
| Neuron sign | Presynaptic neuron treated as wholly excitatory or inhibitory; GABA and glutamate treated as inhibitory | Methods “Neurotransmitter predictions”; this is an assumption and glutamate can vary in effect |
| Input/trials | Poisson stimulation; 30 runs of 1,000 ms for paper experiments | Methods “Computational model”; not a FlyAI training or final-run design |

The paper explicitly limits its model: it assumes zero basal activity and does not represent several neuron and signaling mechanisms (FW-027). Its empirical checks concern its own circuits. The vehicle sensors, left/right motor outputs, adaptation modes, and v783 graph remain new FlyAI modeling choices under ISSUE-003.

## Selected graph transmitter audit — observation only (2026-09-28)

The pinned v2.1.0 annotation joins all 119 selected IDs; 87 have
`top_nt=serotonin`, 21 acetylcholine, and 11 glutamate. None has a
nonblank `known_nt`. The 87 serotonin-predicted neurons supply 123/169
selected outgoing connections. These are classifier outputs, not verified
transmitter identities or synaptic signs (FW-069–FW-071;
`docs/selected_neurotransmitter_audit.md`). The prediction authors
specifically warn about sensory serotonin mispredictions, and their six
predicted classes do not include histamine (FW-070). This evidence does
not establish the true transmitter of any selected ocellar cell.

Applying Shiu et al.'s binary source convention to this different v783
subnetwork would be a **new FlyAI assumption**, including any treatment
of serotonin and receptor-dependent glutamate effects. The project has
not selected one. The concrete routes, tradeoffs, and virtual interface
checks are in `docs/p2_model_route_packet.md`. The P2 anatomical gate passed;
the P4 model/mapping gate remains open. A checked sparse anatomy reader is
documented in `docs/p4_graph_interface.md`, but it does not choose dynamics,
signs, or virtual sensor/motor mappings.

An explicitly exploratory unsigned response probe is documented in
`docs/p4_unsigned_rate_probe.md`. Its count normalization, relaxation,
side-matched input, and zero state are software assumptions used to inspect
four output traces. They are not Shiu et al.'s LIF dynamics, validated
transmitter effects, a motor decoder, or an owner-selected P4 model. Later
exploratory wheel mappings and a moving-cue software smoke are recorded in
`docs/p4_center_cancellation.md` and `docs/p4_dynamic_smoke.md`; those
attempts do not select this probe as the P4 model or validate control.
