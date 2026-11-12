from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        prezzo_medio = []
        for distributore in self._distributori:
            prezzi = PrezzoDAO.get_prezzi(distributore.id)
            if prezzi is not None:
                prezzi_mese=[]
                for prezzo in prezzi:
                    if int(prezzo.data.month) == mese:
                        prezzi_mese.append(prezzo.prezzo_litro)
                if len(prezzi_mese) > 0:
                    media = sum(prezzi_mese)/len(prezzi_mese)
                    prezzo_medio.append((distributore.nome, media))
        return prezzo_medio


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)


    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """

        if giorno < 8:
            for distributore in self._distributori:
                costo = 100 * prezzi_settimana[distributore.id][giorno-1]
                if ultimo_distributore is not None and distributore.id != ultimo_distributore.id:
                    costo += 5
                sequenza = sequenza_parziale+[distributore.id]
                self.__ricorsione(sequenza, giorno+1, distributore, costo_corrente+costo, prezzi_settimana)

        else:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale



    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_prima_settimana_mese = {}
        for distributore in self._distributori:
            prezzi = PrezzoDAO.get_prezzi(distributore.id)
            if prezzi is not None:
                prezzi_prima_settimana_mese[distributore.id]= []
                prezzi.sort(key=lambda prezzo: prezzo.data.day)
                for prezzo in prezzi:
                    if int(prezzo.data.month) == mese:
                        if int(prezzo.data.day) in range(1,8):
                            prezzi_prima_settimana_mese[distributore.id].append(prezzo.prezzo_litro)
        return prezzi_prima_settimana_mese

