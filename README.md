# ProjectOne

APP za hendlovanje porudzbina od strane registrovanih usera.

Za pokretanje APP potrebno je pokrenuti scriptu initialize_files.py prvo koja kreira fajlove za upis i dodaje inicijalno 20-ak proizvoda u katalog.

Svaki user ce se prvo moci registrovati koristeci svoj username i email. Email adresa mora biti jedinstvena dakle ne mogu postojati dva ili vise Usera 
sa istom email adresom. Ukoliko je pri registraciji koriscen email koji je vec u fajlu, odbiti takvu registraciju.

Nakon uspesne registracije, User se moze ulogovati koristeci svoje podatke.

Nakon logovanja gde se mora validirati username i email, User moze prolaziti kroz neku vrstu kataloga proizvoda koji se mogu naci u ponudi.

Podaci o korisnicima ce se cuvati u .txt fajlu.

Katalog proizvoda ce biti predstavljen u jednom excel fajlu ili txt fajlu. Za svaki proizvod bice Naziv proizvoda, Cena i Kolicina na stanju.

Svaki user ce pri registraciji dobiti i jedan kupon sa jedinstvenim brojem koji predstavlja 5% popusta koji moze da se iskoristi pri bilo kojoj kupovini. 
Pored toga postoji i Wholesale popust koji se stice kada visina racuna predje odredjenu cifru i on iznosi 15%. Pri tom ne mogu se odjednom iskoristiti oba popusta.

Nakon kreirane porudzbine korisniku se moze odstampati racun sa navedenim artiklima i cenama, ukupnom cenom, datum prodaje itd. isto tako se moze ponuditi 
da se kreira excel file sa istim tim podacima.

Kreirane porudzbine cuvace se u posebnom fajlu gde ce biti informacija o proizvodima, ukupnoj ceni i korisniku koji je porucio.

Aplikacija pruza mogucnost preuzimanja izvestaja ukoliko imate admin kredencijale. Izvestaji su sledeci:
broj porudbina, isnos svih porudzbina, najpopularniji artikli, iskorisceni kuponi i useri koji su ga iskoristili itd.
Admin moze dodati i promeniti postojece Proizvode.

Za kreiranje Usera, Narudzbine, Kupona i Proizvoda koriste se klase.
