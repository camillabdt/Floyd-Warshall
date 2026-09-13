"""Redes sintéticas reproduzíveis: pesos são custos abstratos, não dados reais."""
import csv
import json
from pathlib import Path
from random import Random


def generate():
    destination = Path('datasets')
    destination.mkdir(exist_ok=True)
    scenarios = [
        ('rede_logistica_30', 30, .10, 2026, False),
        ('rede_urbana_60', 60, .065, 2027, False),
        ('rede_regional_100', 100, .035, 2028, False),
        ('rede_desconexa_40', 40, .08, 2029, True),
    ]
    manifest = []
    for name, n, probability, seed, disconnected in scenarios:
        rng = Random(seed)
        vertices = [f'P{i:03d}' for i in range(1,n+1)]
        edges = {}
        groups = [vertices[:25],vertices[25:38],[vertices[38]],[vertices[39]]] if disconnected else [vertices]
        for group in groups:
            if len(group) > 1:
                # Anel dirigido garante alcance entre todos os nós do grupo.
                for i,u in enumerate(group):
                    edges[u,group[(i+1)%len(group)]] = rng.randint(2,25)
            for u in group:
                for v in group:
                    if u != v and rng.random() < probability:
                        edges.setdefault((u,v),rng.randint(2,50))
        payload = {'vertices':vertices, 'edges':[{'source':u,'target':v,'weight':w} for (u,v),w in sorted(edges.items())]}
        (destination/f'{name}.json').write_text(json.dumps(payload,indent=2)+'\n')
        if not disconnected:
            with (destination/f'{name}.csv').open('w',newline='') as output:
                writer=csv.DictWriter(output,fieldnames=['source','target','weight'])
                writer.writeheader();writer.writerows(payload['edges'])
        manifest.append({'name':name,'vertices':n,'edges':len(edges),'seed':seed,
                         'extra_edge_probability':probability,'strongly_connected':not disconnected})
    return manifest


if __name__ == '__main__':
    print(json.dumps(generate(),indent=2))
