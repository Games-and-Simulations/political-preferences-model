import numpy
from inspect import getfullargspec
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.model_selection import ShuffleSplit
import utils
import datetime
import inspect

class Estimator:
    
    def __init__(self, create_model):
        self.metrics_record = {}
        self.fold_score = []   # progress of fold evaluation     
        self.create_model = create_model
        self.model = None


    def save_model_to_file(self, filename='model_'):
        datestring = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        self.model.save('model/'+ filename + datestring + '.h5')
        
        file = open('model/'+ filename + datestring + '.txt', 'w')        
        try:
            file.write('Epochs: ' + str(self.epochs) + ', Batchsize: ' + str(self.batch_size) +
                       ', n_Splits: ' + str(self.n_splits) + '\n')
        except AttributeError:
            file.write('Epoch,Batchsize,n_Splits info not recorded in estimator')
        for line in inspect.getsourcelines(self.create_model)[0]: 
            file.write(line)
        file.close()



    def create_model_wrapper(self, model_parameters=dict()):
        '''
        Wrapper function for create_model function.
        Creates and stores model based on given parameters.
        DOES NOT CHECK whether parameters make sense.
        '''
        numpy.random.seed(42)
        self.model = getattr(self, 'create_model')(**model_parameters)
        return self.model
    

    def train(self, inputset, outputset, epochs, batch_size, model_parameters=dict()):
        self.epochs = epochs
        self.batch_size = batch_size
                
        self.create_model_wrapper(model_parameters)
            
        fitted = self.model.fit(inputset, outputset, epochs=epochs, batch_size=batch_size)
        self.store_fit_results(fitted)
         
        return self.model             


    def train_crossval(self, inputset, outputset, split, epochs, batch_size, model_parameters=dict()):
        '''
        Train model created throught self.create_model function with given parameters.

        '''
        self.n_splits = split.n_splits
        self.epochs = epochs
        self.batch_size = batch_size      
        self.fold_score = []

        for train_index, test_index in split.split(inputset):             
            self.create_model_wrapper(model_parameters)
            
            in_train, in_test = inputset[train_index], inputset[test_index]
            out_train, out_test = outputset[train_index], outputset[test_index]

            fitted = self.model.fit(in_train, out_train, epochs=self.epochs, batch_size=self.batch_size)
            self.store_fit_results(fitted)
            
            scores = self.model.evaluate(in_test, out_test)
            print(scores)
            
            self.fold_score.append(scores)
         
        return numpy.mean(a=self.fold_score, axis=0)
    
    
    
    def learning_rate(self, inputset, outputset, split, epochs, batch_size, 
                      n_divisions=10, model_parameters=dict()):
        self.n_splits = split.n_splits
        self.epochs = epochs
        self.batch_size = batch_size      
        self.fold_score = []

        for train_index, test_index in split.split(inputset):             
            self.create_model_wrapper(model_parameters)
            
            in_train, in_test = inputset[train_index], inputset[test_index]
            out_train, out_test = outputset[train_index], outputset[test_index]

            
            divisions = utils.generate_subset_divisions(n_divisions, len(in_train))
            in_train_subsets = numpy.split(ary=in_train, indices_or_sections=divisions)
            out_train_subsets = numpy.split(ary=out_train, indices_or_sections=divisions)

            scores_arr = []
            for in_subset, out_subset in zip(in_train_subsets, out_train_subsets):
                self.model.fit(in_subset, out_subset, epochs=epochs, batch_size=batch_size)
            
                scores = self.model.evaluate(in_test, out_test)
                scores_arr.append(scores)
                
            self.fold_score.append(scores_arr)     
                
        return numpy.mean(a=self.fold_score, axis=0)        
    
    
    
    def save_prediction_to_file(self, inputset, metadata, filename):
        '''
        Spocte predikci modelu pro všechny radky v inputset,
        prida metadata a ulozi.
        
        :param inputset: Numpy array s shape odpovidajici modelu
        :param metadata: Numpy array s udaji o obec, momc, okrsek
        :param filename: Cesta k souboru.
        '''
        result = self.model.predict(inputset)
        result = numpy.dot(result, 100)
        result = numpy.concatenate((metadata, result), axis=1)
        numpy.savetxt(fname=filename, X=result, fmt='%0.2f' , delimiter=',')
        return result  
    
   
    def draw_loss_and_metrics(self, ignore_first_n=0, nrows=1, ncols=2, size=(16,6)):
        '''
        Nakresli vyvoj metrik (a ztratove funkce) do zvlastnich grafu v jednom obrazku.
        
        :param ignore_first_n: Nevykresli prvnich n zaznamu.
        :param nrows: Pocet grafu ve sloupci.
        :param ncols: Pocet grafu v radku.
        :param size: Celkova velikost v palcich.
        '''
        color = ['b','r','g','k','o']
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
        fig.set_size_inches(size)
        axes = axes.flatten().tolist()
        for idx, metric in enumerate(self.metrics_record):
            axes[idx].plot(range(self.epochs*self.n_splits - ignore_first_n), 
                 self.metrics_record[metric][ignore_first_n:],
                 color=color[idx % len(color)], linestyle='-', lw=2)
            axes[idx].set_xlabel('epocha')
            axes[idx].set_ylabel(str(metric))
        fig.legend(handles=[mpatches.Patch(color=color[idx % len(color)], label=str(metric))], prop={'size':9})
        plt.show()
        fig.savefig('graphs/LR_'+datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")+'.png')
    
    
    
    
    def draw_metric(self, ignore_first_n=0, size=(15, 10), metric='loss', ylim=False, filepath=False):
        '''
        Nakresli graf vyvoje hodnoty dane metriky (jako metrika se zde pocita i ztratova funkce)
        pro vsechny probehle epochy, kde
        pocet epoch = pocet epoch ve podmnozine cross-validace * pocet podmnozin
        
        :param ignore_first_n: Ignoruj prvnich n epoch.
        :param size: Dvojice hodnot velikosti grafu v palcich.
        :param metric: Pouzita metrika.
        :param ylim: Dvojice hodnot osy y.
        '''
        fig = plt.figure(figsize=size)
        ax1 = fig.add_subplot(111)        

        if ylim:
            ax1.set_ylim(ylim)
        
        ax1.plot(range(self.epochs*self.n_splits - ignore_first_n),
                 self.metrics_record[metric][ignore_first_n:self.epochs*self.n_splits], linestyle='-', lw=2)
        ax1.set_xlabel('epocha')
        ax1.set_ylabel(str(metric))
        plt.show()
        if filepath:
            fig.savefig(filepath + '.png')
        
        
        
        
    def draw_metric_across_folds(self, ignore_first_n=0, size=(15, 10), metric='loss',  ylim=False, filepath=False):
        '''
        Nakresli graf vyvoje hodnoty dane metriky (jako metrika se zde pocita i ztratova funkce)
        pro vsechny epochy. Vyvoj na kazde podmnozine cross-validace je zobrazen jinou barvou.
        
        :param ignore_first_n: Ignoruj prvnich n epoch.
        :param size: Dvojice hodnot velikosti grafu v palcich.
        :param metric: Pouzita metrika.
        :param ylim: Dvojice hodnot osy y.
        '''
        fig = plt.figure(figsize=size)
        ax1 = fig.add_subplot(111)
        
        if ylim:
            ax1.set_ylim(ylim)
        
        ax1.plot(range(self.epochs - ignore_first_n), 
                 self.metrics_record[metric][ignore_first_n:self.epochs], linestyle='-', lw=2)
        for i in range(1, self.n_splits):
            ax1.plot(range(self.epochs), 
                     self.metrics_record[metric][i*self.epochs:(i+1)*self.epochs], linestyle='-', lw=2)
        ax1.set_xlabel('epocha')
        ax1.set_ylabel(str(metric))
        plt.show()
        if filepath:
            fig.savefig(filepath + '.png')
            
            
            
    
    def store_fit_results(self, fitted):
        '''
        Ulozi vyvoj metrik/ztratove funkce pres treninkove epochy do self.metrics_record.
        
        :param fitted: Vyvoj metriky, jak ho vrati metoda model.fit().
        '''
        for metric in fitted.history:
            if metric not in self.metrics_record:
                self.metrics_record[metric] = []
            self.metrics_record[metric].extend(fitted.history[metric])
        
    
    
    
    def gridsearch(self, inputset, outputset, split, epochs, batch_sizes, param_grid=dict()):
        '''
        Trenuje modely vsech moznych konfiguraci zadanych slovnikem argumentu funkce
        vytvarejici model (create_model(...)), ktera byla poskytnuta Estimatoru v dobe jeho vytvoreni.
        Budou vyzkouseny vsechny kombinace poctu epoch, batch_size a argumentu funkce create_model(...) 
        danych v param_grid.
        Funkce vraci seznam vysledku vsech modelu, index nejlepsiho modelu v tomto seznamu (vysledek
        s nejnizsi hodnotou ztratove funkce) a vysledek tohoto nejlepsiho modelu.
        
        Pouziti
        -------
        Pro funkci 'create_model(neurons, layers)'
        
        gridsearch(inputset, outputset, sklearn.model_selection.KFold(n_splits=10),
                   epochs=[10,100], batch_sizes=[50],
                   param_grid={neurons: [10,20], layers: [5,10,15]})
        
        
        :param inputset: Trenovaci vstupni data. 
        :param outputset: Trenovaci vystupni data.
        :param split: Splitter objekt z sklearn.model_selection, ktery ridi rozdeleni
            mnoziny dat pro ucely cross-validace.
        :param epochs: Integer nebo list integeru s pocty epoch.
        :param batch_sizes: Integer nebo list integeru s batch_sizes.
        :param param_grid: Slovnik argumentu funkce create_model(...) obsahujici
            listy s hodnotami techto argumentu.
        '''
        def try_model_parameter(inputset, outputset, args, param_grid, selected_params, epoch, batch_size, results, counter):
            '''
            Tato rekurzivni funkce trenuje modely podle zadanych parametru a ulozi vysledek
            '''
            if not args:
                # all arguments exhausted - search now
                result = self.train(inputset, outputset, split, epoch, batch_size, selected_params)
                
                print('\n', selected_params, counter,'\n')
                counter += 1
                
                output = {'RESULT':result, 'epoch':epoch, 'batch_size':batch_size} 
                output.update(selected_params)                  
                results.append(output)
                return
                
            arg = args.pop()
            if (arg in param_grid):
                for param in param_grid[arg]:
                    selected_params[arg] = param
                    try_model_parameter(inputset, outputset, args, param_grid, selected_params, epoch, batch_size, results, counter)
                del selected_params[arg]
                args.append(arg)
            else:
                raise ValueError('Creator function argument and search parameter mismatch')

        def find_best_result(search_results):
            '''
            Vrati nejlepsi vysledek v search_results a jeho index.
            '''
            min_index = 0
            min_result = search_results[0]['RESULT']
            best = search_results[0]
            for idx, result_dict in enumerate(search_results):
                search_results[idx]['idx'] = idx
                if (result_dict['RESULT'] < min_result):
                    min_result = result_dict['RESULT']
                    min_index = idx
                    best = result_dict
            return min_index, best
        
        search_results = []
        # get list of argument names of model creator function
        args = getfullargspec(self.create_model)[0]
        for e in list(epochs):
            for b in list(batch_sizes):
                try_model_parameter(inputset, outputset, args, param_grid, dict(), e, b, search_results, 1)
                
        idx, best = find_best_result(search_results)
        return search_results, idx, best
    