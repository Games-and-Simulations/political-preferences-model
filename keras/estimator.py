import numpy
from inspect import getfullargspec
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ShuffleSplit
from keras.wrappers.scikit_learn import KerasRegressor
from keras.wrappers.scikit_learn import KerasClassifier
import utils
import datetime
import inspect

class Estimator:
    
    def __init__(self, create_model, description=''):
        self.description = description  # voluntary description of data/model
        self.metrics_record = {}
        self.fold_score_progress = []   # progress of fold evaluation     
        self.create_model = create_model



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
    
    


    def train(self, inputset, outputset, split, epochs, batch_size, model_parameters=dict()):
        '''
        Train model created throught self.create_model function with given parameters.
        If datasets are not given, use default data stored in Estimator.
        
        Creates new model every time it is called.
        '''
        self.create_model_wrapper(model_parameters)
        self.n_splits = split.n_splits
        self.epochs = epochs
        self.batch_size = batch_size      
        self.fold_score_progress = []

        for train_index, test_index in split.split(inputset):    
            in_train, in_test = inputset[train_index], inputset[test_index]
            out_train, out_test = outputset[train_index], outputset[test_index]
            
            fitted = self.model.fit(in_train, out_train, epochs=self.epochs, batch_size=self.batch_size)
            self.store_fit_results(fitted)
            
            scores = self.model.evaluate(in_test, out_test)
            self.fold_score_progress.append(scores)
        return numpy.mean(a=self.fold_score_progress, axis=0)




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




    def get_LR(self, inputset, outputset, subset_in_perc, test_size, split, epochs, batch_size, model_parameters=dict()):
        '''
        Trenuje identicky model vicekrat na ruznych podmnozinach trenovacich dat.
        
        Nejprve rozdeli data na testovaci a trenovaci cast podle parametru test_size.
        
        
        :param inputset: Vstupni data (priklady).
        :param outputset: Vystupni data (priklady).
        :param subset_in_perc: List hodnot pomeru podmnoziny vuci celkove mnozine dat (v procentech). 
            Napr. range(10,101,10
        :param test_size: Pomer testovaci mnoziny vuci celku.
        :param split: Splitter objekt z sklearn.model_selection, ktery ridi rozdeleni
            mnoziny dat pro ucely cross-validace.
        '''
        self.create_model_wrapper(model_parameters)
        self.epochs = epochs
        self.batch_size = batch_size
        self.n_splits = split.n_splits
        nMetrics = 1 + len(self.model.metrics)
        shuffle_split = ShuffleSplit(n_splits=1, test_size=test_size)
        subset_score_progress = numpy.array([])
        
        # rozdel data na teninkovou a testovaci cast
        for train_idx, test_idx in shuffle_split.split(inputset):
            print('Training set: ', len(train_idx), '| Test set: ', len(test_idx))
            in_train, in_test = inputset[train_idx], inputset[test_idx]
            out_train, out_test = outputset[train_idx], outputset[test_idx]
                
            for share in subset_in_perc:
                in_subset, out_subset, set_size = utils.create_data_subset(in_train, out_train, subset=share)
                self.train(in_subset, out_subset, split, epochs, batch_size, model_parameters)
                
                scores = self.model.evaluate(in_test, out_test)
                subset_score_progress = numpy.append(subset_score_progress, numpy.array(scores))
            
        subset_score_progress = subset_score_progress.reshape(int(subset_score_progress.size / nMetrics), nMetrics)
        return subset_score_progress




    def plot_LR(self, scores1, subset_sizes, scores2=[], scores3=[],
                label1='', label2='', label3='', subset_sizes2=[], subset_sizes3=[], filepath=False):
        '''
        Evalute scores for subsets of given sizes and plot them into graph.
        This shows how the prediction changes with change in size of the dataset. (learning rate)
        The graph contains 3 lines - mean score on cross-validation test data,
        score on subsets, score on the entire dataset 
        '''
        
        nMetrics = 1 + len(self.model.metrics)
        metric_functions = self.model.metrics
        metric_functions.insert(0, self.model.loss)

        fig, axes = plt.subplots(nrows=1, ncols=nMetrics)
        fig.set_size_inches(16,4)
        axes = axes.flatten().tolist()
        for idx, metric_fun in enumerate(metric_functions):
            axes[idx].plot(subset_sizes, scores1[:,idx], 'r', label=label1)
            if len(scores2) > 0:
                axes[idx].plot(subset_sizes2, scores2[:,idx], 'b', label=label2)
            if len(scores3) > 0:
                axes[idx].plot(subset_sizes3, scores3[:,idx], 'g', label=label3)
            axes[idx].set_xlabel('Podíl použité trénovací množiny (v %)')
            axes[idx].set_ylabel(str(metric_fun.__name__))
            box = axes[idx].get_position()
            axes[idx].set_position([box.x0, box.y0 + box.height * 0.2,
                 box.width, box.height * 0.8])
        fig.legend(loc='lower center')
        plt.show()
        if filepath:
            fig.savefig(filepath + '.png')
    
    
    
    
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
    