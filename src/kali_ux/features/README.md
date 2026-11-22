# Feature modules

Each feature owns its domain logic and exposes a small public service. Platform operations belong behind `kali_ux.platform`. The initial registry is static; do not add dynamic third-party plugin loading without a separate security design.
