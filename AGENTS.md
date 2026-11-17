# Snagomjer: upute za AI agente

Mobilna aplikacija za bilježenje i analizu treninga snage (FER timski projekt, 5 članova). Opis, pokretanje i način rada: [README.md](README.md). Zahtjevi, arhitektura, model podataka i izračuni: [docs/tehnicki_plan.md](docs/tehnicki_plan.md).

## Jezik

- Dokumentacija, commit poruke, PR-ovi i issueovi: hrvatski.
- Imena u kodu i bazi te komentari u kodu: engleski, kao u modelu podataka (`workout`, `exercise`, `set`).
- Sučelje aplikacije: samo engleski, bez i18n. Brojevi i datumi formatiraju se preko `Intl`, ne ručno.

## Ograničenja

- Podaci samo lokalno (SQLite), rad bez interneta, bez računa i backenda. Nema mrežnih poziva.
- Samo paketi koji rade u Expo Go (iOS se testira samo tako). Paketi se dodaju s `npx expo install`, ne s `npm install`.
- Koristi API-je za verziju Expo SDK-a iz `package.json`. Provjeri dokumentaciju te verzije umjesto da se oslanjaš na pamćenje (npr. expo-sqlite i Expo Router mijenjali su API između verzija).
- Android APK je obavezna isporuka (EAS Build).
- Feature freeze 15.1.2027.: nakon toga samo ispravci.

## Naredbe

```bash
npx expo start              # razvojni server
npm run lint                # ESLint + Prettier
npm run format              # Prettier ispravlja formatiranje
npx tsc --noEmit            # tipovi
npm test                    # Jest
npx drizzle-kit generate    # migracija nakon promjene sheme
```

Prije završetka zadatka moraju proći lint, tipovi i testovi.

## Pravila koda

- Upiti u bazu samo u `src/db/repositories/`. Repozitoriji primaju `db` kao parametar (način testiranja repozitorija je otvoreno pitanje, odj. 13 tehničkog plana).
- Izračuni (volumen, 1RM, rekordi) su čiste funkcije u `src/lib/calculations.ts`, s unit testovima. Zagrijavajuće serije ne ulaze u izračune.
- Ekrani su u `app/` u korijenu repozitorija (Expo Router; ne u `src/app/` kao u Expo predlošku) i ne sadrže upite ni izračune. Podatke čitaju preko hookova iz `src/hooks/`.
- Težina se sprema u kg, vrijeme kao Unix ms. Pretvorba u lb samo pri prikazu i unosu (`src/lib/units.ts`).
- Aktivni trening sprema se odmah: svaka serija upisuje se u bazu čim se potvrdi, ne drži se samo u stanju komponente.
- Strani ključevi u SQLite-u rade samo uz `PRAGMA foreign_keys = ON`, koji se postavlja u `src/db/client.ts`. Kaskadno brisanje i `RESTRICT` ovise o tome.
- Promjena `src/db/schema.ts` uvijek ide s novom migracijom iz `drizzle-kit generate`. Generirane migracije u `drizzle/` se ne uređuju ručno i commitaju se.

## Odluke i otvorena pitanja

- Odjeljci tehničkog plana označeni s **Prijedlog** još nisu konačni. Drži ih se, a ako zadatak traži odstupanje, navedi to u PR-u.
- Ako zadatak ovisi o otvorenom pitanju iz odjeljka 13 tehničkog plana, pitaj umjesto da pretpostaviš.

## Git

- Grana iz `main`: `vrsta/broj-opis`, npr. `feature/12-brzi-unos-serije`, `docs/15-model-podataka`.
- Conventional Commits na hrvatskom: `feat: brzi unos serije`.
- Ne pushati izravno na `main` (GitHub to odbija). Promjene idu kroz PR; CI mora proći i PR mora odobriti Ivan Mitar ili voditelj tima Josip Pavlić (CODEOWNERS, dovoljno je jedno odobrenje). Ne koristi bypass. Autor spaja squash mergeom, pa naslov PR-a mora biti u obliku Conventional Commits.
- Dokumentacija nema posebnu granu, ide istim putem kao kod.
- Bez atribucije AI alata u commitima i PR-ovima (`Co-Authored-By`, "Generated with …").

## Održavanje dokumentacije

Kad promjena uvede ili promijeni naredbu, mapu, paket, pravilo koda, arhitekturu, ograničenje ili rok, u istom PR-u ažuriraj ovu datoteku i, ako treba, README i tehnički plan. Zastarjele napomene makni. Ovdje piši samo ono što se ne vidi iz koda.
