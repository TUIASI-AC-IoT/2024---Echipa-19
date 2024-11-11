# 2024---Echipa-19
# Controlul fluxului prin intermediul unui protocol cu fereastra glisanta

**1. Modul socket**
   - un modul socket abstractizeaza detaliile complexe ale protocoalelor de retea intr-un set de apeluri de sistem
     simplificate, programele fiind capabile sa comunice in retea, indiferent de detaliile subiacente ale stivelor
     de comunicatie
     
**2.Solutie de tip remote storage**
- Server Storage:
  - va asculta cererile de la client
  - va permite operatii de stocare si manipulare a fisierelor (upload,download,delete,move)
  - va gestiona fluxul de date folosind un mecanism de fereastra glisanta
  
- Client:
    - va trimite un numar fix de mesaje(dimensiunea ferestrei) si va astepta confirmarea de la server
    - va trimite cereri la server pentru a efectua operatii, fiecare cerere ar putea include tipul de operatie si, eventual,numele fisierului si datele asociate
    - va implementa logica necesara pentru a permite utilizatorului sa interactioneze cu fisierele de pe server

**3. Protocol UDP**
   - nu este orientat pe conexiune
   - mod de asociere intuitiv
   - formatul mesajelor utilizate trebuie sa contina un camp prin intermediul caruia se numeroteaza datagramele
     folosind numere de secventa unice
   - mecanism de comunicatie pas cu pas si temporizare a receptiei pentru a facilita primirea datagramelor in
     ordinea in care au fost transmise

**4. Implementare mecanism cu fereastra glisanta varianta go-back-n**
   - clientul trimite o serie de mesaje si asteapta confirmare de la server pentru cel putin primul
     mesaj din fereastra
   - fiecare mesaj trimis de client va include un numar de secventa
   - server-ul va trimire o confirmare pentru fiecare mesaj primit corect

**5. Fire de executie**
   - fir de excutie pentru interfata grafica si transmisie
   - fir de executie pentru receptie
   - fir de executie pebtru timeout


![fire executie](https://github.com/user-attachments/assets/6a8cad3c-6e2f-47e2-b2d0-77aae7647a37)


**6. Mecanici de interactiune**
   * Comunicare prin socket-uri : utilizarea socket-urilorUDP pentru transferul rapid al datelor
                                  intre client si server
   * Operatiuni CRUD:
     - crearea : incarcarea fisierelor pe server
     - citire: descarcarea fisierelor existente
     - actualizare: modificarea fisierelor
     - stergere: eliminarea fisierelor
   * Feedback si confirmari: ACK, confirmari de receptie a pachetelor
   * Gestionare timeout-urilor: monitorizarea timpului de asteptare pentru confirmari si retransmiterea pachetelor daca este necesar
   * Interfata cu utilizatorul: comenzi de la utilizator pentru operatiuni, cu feedback vizual privind starea transferurilor
   * Protocolul ferestrei: trimiterea mai multor pachete intr-o fereastra, cu ajustarea dimensiunii ferestrei in functie de conditiile retelei
   * Gestionarea erorilor: logarea erorilor si implementarea mecanismelor de recuperare din erori
   * Definirea pachetelor: stabilirea unui format standard pentru pachete, inclusiv numere de secventa si chekcum-uri

     
  **7. Tipuri de pachete**
  Data : In cadrul protocolului UDP pentru a transmite un pachet de tip Data vom avea nevoie de un numar de secventa, ce va indica indicele corespunzator al mesajului
  
  ACK : Pachetul ACKnowledge va contine un numar de secventa corespunzator mesajului pentru care se trimite confirmarea, facilitand astfel comunicarea intre server si client
  
  Operatii : Pachetul corespunzator operatiilor ce vor fi efectuate asupra datelor va contine tipul de operatie ce va fi aplicata asupra fisierelor


  ![image](https://github.com/user-attachments/assets/2f55cf13-325c-4096-9bc6-f51d58c1bb99)

