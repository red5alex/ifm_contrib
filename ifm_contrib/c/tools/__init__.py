def plot_density_model(alpha, c_ref, c_max, rho_ref, NaCl=True):

    import matplotlib.pyplot as plt

    # calculate rho_max
    rho_max = rho_ref + alpha * (c_max - c_ref)

    # plot density model
    fig, ax1 = plt.subplots(1)
    ax1.plot([c_ref, c_max], [rho_ref, rho_max], "o-", label="modelled density")

    if NaCl:
        rho_max_NaCl = 1000 +  0.045 * (35000 - 0)
        ax1.plot([0, 35000], [1000, rho_max_NaCl], "--", color="grey", label="typical NaCl")

    ax1.grid()
    ax1.set_ylabel(u"Density [kg/m³]")
    ax1.set_xlabel(u"Concentration [mg/l]")

    ax1.vlines(c_ref, rho_ref, rho_max, linestyle="--", color="green", label="Reference Concentration")
    ax1.vlines(c_max, rho_ref, rho_max, linestyle="--", color="red", label="Maximum Concentration")

    ax1.hlines(rho_ref, c_ref, c_max, linestyle=":", color="green", label="Reference Density")
    ax1.hlines(rho_max, c_ref, c_max, linestyle=":", color="red", label="Maximum Density")

    ax1.legend()

    return ax1
