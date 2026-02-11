"""
Streamlit app: Schwarzschild radius of a black hole compared to solar system scales.
Created with help from Cursor Agent for Astronomy 1221.
"""
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# Physical constants (SI)
G = 6.67430e-11   # m³ kg⁻¹ s⁻²
c = 299_792_458   # m/s
M_sun_kg = 1.989e30  # kg

# Schwarzschild radius for 1 M_sun in km
R_sun_schwarzschild_km = 2 * G * M_sun_kg / (c ** 2) / 1000  # ~2.95 km

# Solar system: orbital radii (semi-major axis) in km
AU_KM = 149_597_870.7
ORBITS_KM = {
    "Mercury": 0.387 * AU_KM,
    "Venus": 0.723 * AU_KM,
    "Earth": 1.0 * AU_KM,
    "Mars": 1.524 * AU_KM,
    "Ceres": 2.766 * AU_KM,
    "Jupiter": 5.203 * AU_KM,
    "Saturn": 9.537 * AU_KM,
    "Uranus": 19.19 * AU_KM,
    "Neptune": 30.07 * AU_KM,
    "Pluto": 39.48 * AU_KM,
    "Makemake": 45.43 * AU_KM,
    "Eris": 67.86 * AU_KM,
}

# For small black holes: physical radii in km
SUN_RADIUS_KM = 695_700
JUPITER_RADIUS_KM = 69_911
EARTH_RADIUS_KM = 6_371
MOON_RADIUS_KM = 1_738  # Earth's moon
PLUTO_RADIUS_KM = 1_188
CERES_RADIUS_KM = 476
VESTA_RADIUS_KM = 262
ENCELADUS_RADIUS_KM = 252  # Saturn's moon Enceladus
EROS_RADIUS_KM = 8.4  # asteroid Eros
HALLEY_NUCLEUS_KM = 11  # characteristic radius ~11 km (15×8×8 km nucleus)
NEUTRON_STAR_RADIUS_KM = 10  # typical neutron star radius ~10 km

# Sun drawn only when R_s >= this fraction of Sun radius
SUN_MIN_FRACTION = 0.1

# Threshold: half of Mercury's orbital radius
HALF_MERCURY_ORBIT_KM = 0.5 * ORBITS_KM["Mercury"]

# Use AU when event horizon > this (0.05 AU in km)
AU_SWITCH_KM = 0.05 * AU_KM


def schwarzschild_radius_km(mass_solar):
    """Schwarzschild radius in km for given mass in solar masses."""
    return R_sun_schwarzschild_km * mass_solar


def _format_dist(r_km, use_au):
    """Format distance for labels; use_au means r_km is actually in km but we display in AU."""
    if use_au:
        r_au = r_km / AU_KM
        return f"{r_au:.3g} AU"
    if r_km >= 1e6:
        return f"{r_km/1e6:.2f} Mkm"
    if r_km >= 1000:
        return f"{r_km/1000:.1f}k km"
    return f"{r_km:.0f} km"


def plot_large_black_hole(ax, R_s_km, use_au):
    """Plot event horizon (outline only) and at most one orbit smaller, at most two larger than R_s."""
    orbit_names = list(ORBITS_KM.keys())
    orbit_radii = list(ORBITS_KM.values())
    scale = AU_KM if use_au else 1.0
    R_s = R_s_km / scale  # in AU if use_au else km

    # At most one smaller: largest orbit with r < R_s
    smaller_name, smaller_r = None, None
    for name, r in zip(orbit_names, orbit_radii):
        r_scaled = r / scale
        if r_scaled < R_s:
            smaller_name, smaller_r = name, r_scaled

    if smaller_r is None and not use_au:
        # Sun radius as fallback when R_s is huge (only in km mode)
        smaller_name, smaller_r = "Sun (radius)", SUN_RADIUS_KM / scale

    # At most two larger: two smallest orbits with r > R_s
    larger_list = []
    for name, r in zip(orbit_names, orbit_radii):
        r_scaled = r / scale
        if r_scaled > R_s:
            larger_list.append((name, r_scaled))
    larger_list.sort(key=lambda x: x[1])
    larger_list = larger_list[:2]
    if not larger_list and R_s > 0:
        larger_list = [("1.2 × R_s (scale)", R_s * 1.2)]

    max_plot_r = R_s * 1.2
    if smaller_r is not None:
        max_plot_r = max(max_plot_r, smaller_r * 1.1)
    for _, r in larger_list:
        max_plot_r = max(max_plot_r, r * 1.1)
    lim = max_plot_r * 1.05

    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)

    # Event horizon: outline only (no fill) so smaller objects remain visible
    circle_bh = mpatches.Circle((0, 0), R_s, fill=False, edgecolor="black", linewidth=2.5, zorder=10)
    ax.add_patch(circle_bh)
    ax.plot(0, 0, "k+", markersize=10, zorder=11)

    unit = "AU" if use_au else "km"
    if smaller_r is not None:
        circle_small = mpatches.Circle((0, 0), smaller_r, fill=False, edgecolor="C0", linewidth=2, linestyle="--", label=f"{smaller_name} ({_format_dist(smaller_r * scale, use_au)})")
        ax.add_patch(circle_small)
    for i, (name, r) in enumerate(larger_list):
        color = "C1" if i == 0 else "C2"
        circle = mpatches.Circle((0, 0), r, fill=False, edgecolor=color, linewidth=2, linestyle="--", label=f"{name} ({_format_dist(r * scale, use_au)})")
        ax.add_patch(circle)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlabel(f"Distance ({unit})")
    ax.set_ylabel(f"Distance ({unit})")
    ax.set_title(f"Event horizon (black circle): R_s = {_format_dist(R_s_km, use_au)}")


def plot_small_black_hole(ax, R_s_km, use_au):
    """Plot event horizon (outline only) and at most one object smaller, at most two larger than R_s."""
    scale = AU_KM if use_au else 1.0
    R_s = R_s_km / scale

    # R_s < 0.1 Sun: Eros, neutron star, Enceladus, Vesta, Ceres, Moon, Earth (at most 1 smaller, 2 larger)
    if R_s_km < SUN_MIN_FRACTION * SUN_RADIUS_KM:
        refs = [
            ("Eros (asteroid)", EROS_RADIUS_KM),
            ("Neutron star (typical radius)", NEUTRON_STAR_RADIUS_KM),
            ("Enceladus (moon of Saturn)", ENCELADUS_RADIUS_KM),
            ("Vesta (asteroid)", VESTA_RADIUS_KM),  # ~263 km
            ("Ceres (dwarf planet)", CERES_RADIUS_KM),  # ~470 km
            ("Moon (Earth's moon)", MOON_RADIUS_KM),
            ("Earth (radius)", EARTH_RADIUS_KM),
        ]
        smaller = [(name, r / scale) for name, r in refs if r < R_s_km]
        larger = [(name, r / scale) for name, r in refs if r > R_s_km]
        smaller.sort(key=lambda x: x[1], reverse=True)
        larger.sort(key=lambda x: x[1])
        to_draw = smaller[:1] + larger[:2]
        colors = ["darkorange", "silver", "lightblue", "tan", "gray", "lightgray", "steelblue"]
        name_to_color = dict(zip([n for n, _ in refs], colors))
        max_drawn_km = max(r_plot * scale for _, r_plot in to_draw)
        lim_km = max(R_s_km, max_drawn_km) * 1.25
        lim = lim_km / scale
    else:
        # R_s >= 0.1 Sun radius: Jupiter, Earth, Sun, etc.
        refs = [
            ("Neutron star (typical radius)", NEUTRON_STAR_RADIUS_KM),
            ("Halley's comet nucleus", HALLEY_NUCLEUS_KM),
            ("Vesta (asteroid)", VESTA_RADIUS_KM),
            ("Ceres (dwarf planet)", CERES_RADIUS_KM),
            ("Pluto (dwarf planet)", PLUTO_RADIUS_KM),
            ("Earth (radius)", EARTH_RADIUS_KM),
            ("Jupiter (radius)", JUPITER_RADIUS_KM),
        ]
        refs.append(("Sun (radius)", SUN_RADIUS_KM))
        smaller = [(name, r / scale) for name, r in refs if r < R_s_km]
        larger = [(name, r / scale) for name, r in refs if r > R_s_km]
        smaller.sort(key=lambda x: x[1], reverse=True)
        larger.sort(key=lambda x: x[1])
        to_draw = smaller[:1] + larger[:2]
        colors = ["silver", "brown", "tan", "gray", "orange", "steelblue", "sandybrown", "gold"]
        name_to_color = dict(zip([n for n, _ in refs], colors))
        # Scale to largest reference circle actually drawn
        max_drawn_km = max(r_plot * scale for _, r_plot in to_draw)
        lim_km = max(R_s_km, max_drawn_km) * 1.25
        lim = lim_km / scale

    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)

    # Event horizon: outline only, no fill (no label — not in legend)
    circle_bh = mpatches.Circle((0, 0), R_s, fill=False, edgecolor="black", linewidth=2.5, zorder=10)
    ax.add_patch(circle_bh)
    ax.plot(0, 0, "k+", markersize=8, zorder=11)

    legend_handles = []
    for name, r in to_draw:
        r_plot = r  # r in plot units (r_km/scale)
        r_km = r * scale
        color = name_to_color.get(name, "C0")
        circle = mpatches.Circle((0, 0), r_plot, fill=False, edgecolor=color, linewidth=1.5, zorder=5)
        ax.add_patch(circle)
        label = f"{name} ({_format_dist(r_km, use_au)})"
        legend_handles.append(Line2D([0], [0], color=color, linewidth=2, linestyle="-", label=label))
    if legend_handles:
        ax.legend(handles=legend_handles, loc="upper right", fontsize=9)

    unit = "AU" if use_au else "km"
    ax.set_xlabel(f"Distance ({unit})")
    ax.set_ylabel(f"Distance ({unit})")
    ax.set_title(f"Event horizon vs solar system objects (R_s = {_format_dist(R_s_km, use_au)})")
    ax.grid(True, alpha=0.3)


def main():
    st.set_page_config(page_title="Schwarzschild Radius", layout="wide")
    st.title("Black Hole Event Horizon vs. Solar System")

    # Slider is log₁₀(mass in M☉), range 0 to 10 → mass 1 to 10^10 M☉
    log10_mass = st.slider(
        "log₁₀(mass in M☉)",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.1,
        format="%.1f",
        help="Mass = 10^slider M☉ (0 = 1 M☉, 10 = 10¹⁰ M☉)",
    )
    mass_solar = 10 ** log10_mass
    R_s_km = schwarzschild_radius_km(mass_solar)
    use_au = R_s_km > AU_SWITCH_KM
    R_s_display = f"{R_s_km/AU_KM:.4g} AU" if use_au else f"{R_s_km:.4g} km"
    st.markdown(f"**Mass:** {mass_solar:.4g} M☉  →  **Schwarzschild radius:** {R_s_display}")

    fig, ax = plt.subplots(figsize=(8, 8))

    if R_s_km >= HALF_MERCURY_ORBIT_KM:
        plot_large_black_hole(ax, R_s_km, use_au)
    else:
        plot_small_black_hole(ax, R_s_km, use_au)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    with st.expander("Reference values"):
        st.markdown("- **Schwarzschild radius:** R_s = 2GM/c² ≈ 2.95 km for 1 M☉")
        st.markdown("- **Half Mercury orbit:** ≈ 29 million km (threshold for switching comparison mode)")
        st.markdown("- **Sun radius:** ~696,000 km; **Jupiter radius:** ~70,000 km; **Earth radius:** ~6,371 km; **Moon:** ~1,738 km")
        st.markdown("- **Neutron star (typical radius):** ~10 km; **Eros (asteroid):** ~8.4 km (for smallest mass black holes)")
        st.markdown("- **Small/mid-scale (R_s < ~70,000 km):** Eros, neutron star, Enceladus 252 km, Vesta ~263 km, Ceres ~470 km, Moon 1,738 km, Earth 6,371 km")
        st.markdown("- **Orbital radii:** Mercury 58 Mkm, Earth 150 Mkm, Pluto 5.9 billion km, Makemake 45.4 AU, Eris 67.9 AU")
        st.markdown("- **Halley's comet nucleus:** ~11 km; Pluto ~1,188 km radius")


if __name__ == "__main__":
    main()
