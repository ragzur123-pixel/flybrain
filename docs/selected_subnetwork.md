# Selected v783 anatomical subnetwork — 2026-09-28

Rüzgar selected the DNp20+DNp22 output family. This is a directed
archive-derived graph only; sensor encoding, signs, model weights,
motor decoder, and behavioral validity remain open.

- Source rows rescanned: **16,847,997**. Before the role-path filter, the C02 candidate graph had **291** annotated nodes, **958** directed candidate pairs, and **7,259** pair-summed synapses.
- Selected complete-path graph: **119** nodes, **169** directed edges, **4,434** pair-summed synapses.
- Selected roles: {'photoreceptor': 103, 'OCG01': 12, 'DNp20': 2, 'DNp22': 2, 'DNp28': 0}. Weak component sizes: [119].
- Nodes without a directed path to any selected output: **0**. All four outputs also have fully same-side photoreceptor paths.
- The graph retains all biological left/right/center paths that satisfy the two-edge rule; biological side is metadata, not a motor command.
- Config SHA-256: `f91b72d548808bfd02967f7aeaa77d2679dca3ddc7978db092331489906b5b35`. Raw graph SHA-256: `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf`.
- Node CSV SHA-256: `3fe59923fb1afcbd0ce47773d05f63fa59a0cc63433c72aab756ac631f4461d2`. Edge CSV SHA-256: `d69d81db5cbcfdc4300d054853df455fdbfcf2985d87c1e375cafba26ba0b2a4`.
- Machine-readable files: `data/derived/selected_subnetwork_nodes.csv`, `data/derived/selected_subnetwork_edges.csv`, and `data/derived/selected_subnetwork_report.json`.
