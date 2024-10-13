import csv
import top_50


def to_csv(module):
    with open('websites_by_conflicts.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for num_conflict_persona, v in module.WEBSITES_BY_CONFLICTS.items():
            num_websites = len(v)
            writer.writerow([num_conflict_persona, num_websites])

    with open('personas_by_conflicts.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for num_conflict_persona, v in module.PERSONAS_BY_CONFLICTS.items():
            num_personas = len(v)
            writer.writerow([num_conflict_persona, num_personas])

    with open('websites_and_conflict_segments_by_conflicts.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for num_conflict_persona, v in module.WEBSITES_AND_CONFLICT_SEGMENTS_BY_CONFLICTS.items():
            for ws, v2 in v.items():
                for persona, num_conflict_segments in v2.items():
                    writer.writerow([num_conflict_persona, ws, persona, num_conflict_segments])

    with open('persona_and_conflicting_segments_by_conflicts.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for num_conflict_persona, v in module.PERSONA_AND_CONFLICTING_SEGMENTS_BY_CONFLICTS.items():
            for persona, v2 in v.items():
                for ws, num_conflicts in v2.items():
                    writer.writerow([num_conflict_persona, persona, ws, num_conflicts])

    with open('average_conflict_rate_0.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for num_conflict_persona, v in module.AVERAGE_CONFLICT_RATE_0.items():
            writer.writerow([num_conflict_persona, v])

    with open('average_conflict_rate_2.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for num_conflict_persona, v in module.AVERAGE_CONFLICT_RATE_2.items():
            writer.writerow([num_conflict_persona, v])

    if hasattr(module, 'CONFLICT_RATE_0'):
        with open('conflict_rate_0.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            for num_conflict_persona, v in module.CONFLICT_RATE_0.items():
                for ws, rate in v.items():
                    writer.writerow([num_conflict_persona, ws, rate])

    if hasattr(module, 'CONFLICT_RATE_2'):
        with open('conflict_rate_2.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            for num_conflict_persona, v in module.CONFLICT_RATE_2.items():
                for ws, rate in v.items():
                    writer.writerow([num_conflict_persona, ws, rate])


def main():
    to_csv(top_50)


if __name__ == '__main__':
    main()
