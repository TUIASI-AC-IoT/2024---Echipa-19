# 2024---Echipa-19
# Controlul fluxului prin intermediul unui protocol cu fereastra glisanta

Proiectul implementeaza un protocol bazat pe UDP pentru transferul fisierelor si realizarea operatiilor de tip CRUD(Create, Remove, Upload, Download) intre un client si un server. Utilizarea unui mecanism de fereastra glisanta Go-back-N asigura o gestionare eficienta a fluxului de date,gestionand pierderile de pachete si confirmarile pentru acestea.

**1. Modul socket**
   - un modul socket abstractizeaza detaliile complexe ale protocoalelor de retea intr-un set de apeluri de sistem
     simplificate, programele fiind capabile sa comunice in retea, indiferent de detaliile subiacente ale stivelor
     de comunicatie
     
**2.Solutie de tip remote storage**
- Server Storage:
  - asculta cererile de la client
  - permite operatii de stocare si manipulare a fisierelor (upload,download,delete,move)
  - gestionarea fluxului de date printr-un mecanism de confirmare si retransmitere
  
- Client:
    - trimite un numar fix de mesaje(dimensiunea ferestrei) si astepta confirmarea de la server
    - trimite cereri la server pentru a efectua operatii, fiecare cerere include tipul de operatie si numele fisierului asupra caruia se doreste interventia
    - oferirea unei interfete simple pentru utilizator

**3. Protocol UDP**
   - nu este orientat pe conexiune
   - mod de asociere intuitiv
   - formatul mesajelor utilizate trebuie sa contina un camp prin intermediul caruia se numeroteaza datagramele folosind numere de secventa unice
   - mecanism de comunicatie pas cu pas si temporizare a receptiei pentru a facilita primirea datagramelor in ordinea in care au fost transmise

**4. Implementare mecanism cu fereastra glisanta varianta go-back-n**
   - clientul trimite o serie de mesaje si asteapta confirmare de la server pentru cel putin primul mesaj din fereastra
   - fiecare mesaj trimis de client va include un numar de secventa
   - server-ul va trimire o confirmare pentru fiecare mesaj primit corect
   - daca un pachet este pierdut, clientul retransmite toate pachetele incepand cu cel pierdut

**5. Fire de executie**
   - fir de executie pentru transmisie pentru server
   - fir de executie pentru transmisie pentru client
   - fir de executie pentru receptie pentru server
   - fir de executie pentru receptie pentru client

![fire_executie](https://github.com/user-attachments/assets/adcc2969-23b2-4765-9a16-926d9e429d1c)



**6. Mecanici de interactiune**

   * Comunicare prin socket-uri : utilizarea socket-urilorUDP pentru transferul rapid al datelor
                                  intre client si server
   * Operatiuni CRUD:
     - creare : incarcarea fisierelor pe server
     - citire: descarcarea fisierelor existente
     - actualizare : modificarea fisierelor
     - stergere: eliminarea fisierelor sau directoarelor
   * Feedback si confirmari: ACK, confirmari de receptie a pachetelor
   * Gestionare timeout-urilor: monitorizarea timpului de asteptare pentru confirmari si retransmiterea pachetelor daca este necesar
   * Interfata cu utilizatorul: comenzi de la utilizator pentru operatiuni, cu feedback vizual privind starea transferurilor
   * Protocolul ferestrei: trimiterea mai multor pachete intr-o fereastra, cu ajustarea dimensiunii ferestrei in functie de conditiile retelei
   * Gestionarea erorilor: logarea erorilor si implementarea mecanismelor de recuperare din erori
   * Definirea pachetelor: stabilirea unui format standard pentru pachete, care include un header cu numar de secventa si datele asociate

     
  **7. Tipuri de pachete**
  - Mesaj simplu : pachet de date pentru comunicarea intre server si client ("Disconnect" message etc.)
  - ACK : pachetul ACKnowledge contine un numar de secventa corespunzator mesajului pentru care se trimite confirmarea, facilitand astfel comunicarea intre server si client
  - Operatii : pachetul corespunzator operatiilor ce vor fi efectuate asupra datelor contine tipul de operatie ce va fi aplicata asupra fisierului si numele acestuia


  ![image](https://github.com/user-attachments/assets/2f55cf13-325c-4096-9bc6-f51d58c1bb99)

