# LLM Clinical Decision Pipeline

Ovaj projekat služi za evaluaciju odgovora velikih jezičkih modela (LLM) u kontekstu kliničke podrške odlučivanju, uz dodatni sloj bezbednosne logike.

## Cilj projekta

Cilj projekta je da poredi odgovore modela i da, na osnovu definisane politike odlučivanja, svaki odgovor svrsta u jednu od sledećih kategorija:

- ACCEPT
- WARN
- DEFER
- ESCALATE
- REFUSE

Projekat je zamišljen za pitanja medicinskog tipa, odnosno za high-stakes scenarije u kojima nije dovoljno samo porediti tekst odgovora, već je potrebno uvesti i dodatne sigurnosne provere.

## Trenutna verzija

Trenutna verzija koristi dva bazna modela za evaluaciju:

- ChatGPT
- GPT-4

Arhitektura je postavljena tako da se kasnije mogu dodavati i drugi modeli.

## Struktura pipeline-a

Sistem radi kroz nekoliko koraka:

1. **Rule-based detekcija signala rizika**  
   Prepoznaju se obrasci kao što su:
   - traženje doze
   - kontekst trudnoće
   - pedijatrijski kontekst
   - kombinovanje lekova
   - samostalno menjanje terapije
   - visokorizični lekovi

2. **LLM-assisted risk enrichment**  
   Po potrebi se dodaju dodatni strukturisani signali rizika.

3. **Guardrail routing**  
   Za jasno rizične slučajeve primenjuje se short-circuit logika i sistem odmah vraća odluku.

4. **Decision policy layer**  
   Na osnovu prikupljenih signala donosi se finalna sistemska odluka:
   `ACCEPT`, `WARN`, `DEFER`, `ESCALATE` ili `REFUSE`.

5. **Evaluacija i izveštavanje**  
   Rezultati se porede sa očekivanim oznakama iz skupa pitanja.

## Organizacija projekta

- `src/guardrails/rules.py` – detekcija signala rizika
- `src/guardrails/router.py` – short-circuit logika za najrizičnije slučajeve
- `src/guardrails/decision_policy.py` – centralna logika odlučivanja
- `src/compare_models.py` – pokretanje evaluacije nad modelima
- `src/reporting.py` – prikaz rezultata i sažetaka

## Skup pitanja

Benchmark pitanja se nalaze u fajlu:

- `data/clinical_questions.json`

Svako pitanje sadrži očekivanu odluku i očekivani nivo ozbiljnosti.

## Pokretanje projekta

```bash
python -m src.compare_models
```
