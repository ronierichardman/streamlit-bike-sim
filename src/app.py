import simulation as sim


def main():
    durchlaeufen = 10

    sim_ergebnisse = []
    for i in range(durchlaeufen):
        try:
            sim_ergebnis = sim.monte_carlo(preis_pro_stunde=3, experiments=10000)
            sim_ergebnisse.append(sim_ergebnis)
            print(f"Durchlauf {i + 1}:\n{sim_ergebnis}")

        except Exception as e:
            print(f"Fehler bei der Simulation: {e}")
            continue

    print("Simulation abgeschlossen.")


if __name__ == "__main__":
    main()
