import math, time, machine

class HRVAnalysis:
    @staticmethod
    def filter(IBI_list_raw):
        IBI_list = []
        mean_ibi = 0
        for ibi in IBI_list_raw:
            mean_ibi += ibi
        mean_ibi /= len(IBI_list_raw)
        threshold_lower = mean_ibi * 0.7
        if threshold_lower < 300:
            threshold_lower = 300
        threshold_higher = mean_ibi * 1.3
        for i in range(len(IBI_list_raw)):
            if threshold_lower < IBI_list_raw[i] < threshold_higher:
                IBI_list.append(IBI_list_raw[i])
        return IBI_list

    @staticmethod
    def calculate_mean_hr(ibi_list):
        mean_ibi = sum(ibi_list) / len(ibi_list)
        mean_hr = 60000 / mean_ibi
        return round(mean_hr, 2)
    
    @staticmethod
    def calculate_mean_ppi(ibi_list):
        mean_ppi = sum(ibi_list) / len(ibi_list)
        return round(mean_ppi, 2)
    
    @staticmethod
    def calculate_rmssd(ibi_list):
        average = 0
        for i in range(1, len(ibi_list), 1):
            difference = (ibi_list[i] - ibi_list[i - 1]) ** 2
            average += difference
        average /= len(ibi_list) - 1
        rmssd = math.sqrt(average)
        return round(rmssd)
    
    @staticmethod
    def calculate_sdnn(ibi_list):
        if len(ibi_list) < 2:
            return 0
        
        mean_ibi = sum(ibi_list) / len(ibi_list)
        
        squared_diff = [(ibi - mean_ibi) ** 2 for ibi in ibi_list]
        
        variance = sum(squared_diff) / (len(ibi_list) - 1)
        sdnn = math.sqrt(variance)
        return round(sdnn, 2)
    
    @staticmethod
    def estimate_autonomic_balance(rmssd):
    
        if rmssd < 20:
            sns = 0.8  
            pns = 0.2 
        elif rmssd < 50:
            sns = 0.6
            pns = 0.4
        else:
            sns = 0.3 
            pns = 0.7  
        
        return round(sns, 2), round(pns, 2)

    def calculate(self, ibi):
        if len(ibi) < 0:
            return 0
        filtered_ibi = self.filter(ibi)
        mean_hr = self.calculate_mean_hr(filtered_ibi)
        mean_ppi = self.calculate_mean_ppi(filtered_ibi)
        rmssd = self.calculate_rmssd(filtered_ibi)
        sdnn = self.calculate_sdnn(filtered_ibi)
        return {  
            "id": machine.unique_id().hex(),
            "time": int(time.time()),
            "Mean HR": mean_hr,
            "PPI (ms)": mean_ppi,
            "RMSSD": rmssd,
            "SDNN": sdnn,
        }