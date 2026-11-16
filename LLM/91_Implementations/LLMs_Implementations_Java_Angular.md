# Implémentations Pratiques & Code - LLMs en Java et Angular
## Extensions Pratiques du Guide Mathématique

---

# SECTION 7 : IMPLÉMENTATIONS PRATIQUES EN JAVA

## 7.1 Couche Linéaire (Fully Connected)

```java
/**
 * Implémentation d'une couche linéaire (dense)
 * y = W * x + b
 */
public class LinearLayer {
    private double[][] weights;  // W : d_in × d_out
    private double[] bias;        // b : d_out
    private int inputDim;
    private int outputDim;
    
    public LinearLayer(int inputDim, int outputDim) {
        this.inputDim = inputDim;
        this.outputDim = outputDim;
        this.weights = new double[inputDim][outputDim];
        this.bias = new double[outputDim];
        initializeWeights();
    }
    
    /**
     * Initialisation He : variance = 2 / fan_in
     * Important pour ReLU networks
     */
    private void initializeWeights() {
        double stdDev = Math.sqrt(2.0 / inputDim);
        Random rand = new Random();
        
        for (int i = 0; i < inputDim; i++) {
            for (int j = 0; j < outputDim; j++) {
                weights[i][j] = rand.nextGaussian() * stdDev;
            }
        }
        // Bias initialisé à 0
    }
    
    /**
     * Forward pass : y = W^T * x + b
     * @param input vecteur x de dimension inputDim
     * @return output vecteur y de dimension outputDim
     */
    public double[] forward(double[] input) {
        double[] output = new double[outputDim];
        
        // Multiplication matricielle : W^T * x
        for (int j = 0; j < outputDim; j++) {
            output[j] = bias[j];  // Ajouter le bias
            for (int i = 0; i < inputDim; i++) {
                output[j] += weights[i][j] * input[i];
            }
        }
        return output;
    }
    
    /**
     * Backward pass : calcule gradients via backpropagation
     * @param gradOutput gradient de la loss par rapport à output
     * @param input input du forward pass
     * @return gradient par rapport à input
     */
    public double[] backward(double[] gradOutput, double[] input) {
        double[] gradInput = new double[inputDim];
        double[][] gradWeights = new double[inputDim][outputDim];
        double[] gradBias = new double[outputDim];
        
        // dL/db_j = dL/dy_j
        for (int j = 0; j < outputDim; j++) {
            gradBias[j] = gradOutput[j];
        }
        
        // dL/dW_{ij} = dL/dy_j * x_i
        for (int i = 0; i < inputDim; i++) {
            for (int j = 0; j < outputDim; j++) {
                gradWeights[i][j] = gradOutput[j] * input[i];
            }
        }
        
        // dL/dx_i = sum_j (dL/dy_j * W_{ij})
        for (int i = 0; i < inputDim; i++) {
            gradInput[i] = 0;
            for (int j = 0; j < outputDim; j++) {
                gradInput[i] += gradOutput[j] * weights[i][j];
            }
        }
        
        // Mise à jour des poids avec gradient descent
        updateWeights(gradWeights, gradBias, 0.001);  // learning rate = 0.001
        
        return gradInput;
    }
    
    private void updateWeights(double[][] gradWeights, double[] gradBias, double lr) {
        for (int i = 0; i < inputDim; i++) {
            for (int j = 0; j < outputDim; j++) {
                weights[i][j] -= lr * gradWeights[i][j];
            }
        }
        for (int j = 0; j < outputDim; j++) {
            bias[j] -= lr * gradBias[j];
        }
    }
}
```

---

## 7.2 Activation Functions

```java
/**
 * Fonction d'activation ReLU : max(0, x)
 */
public class ReLU {
    public static double[] activate(double[] input) {
        double[] output = new double[input.length];
        for (int i = 0; i < input.length; i++) {
            output[i] = Math.max(0, input[i]);
        }
        return output;
    }
    
    /**
     * Dérivée pour backpropagation
     * ReLU'(x) = 1 si x > 0, 0 sinon
     */
    public static double[] derivative(double[] input) {
        double[] grad = new double[input.length];
        for (int i = 0; i < input.length; i++) {
            grad[i] = input[i] > 0 ? 1 : 0;
        }
        return grad;
    }
}

/**
 * Fonction sigmoid : σ(x) = 1 / (1 + e^(-x))
 */
public class Sigmoid {
    public static double[] activate(double[] input) {
        double[] output = new double[input.length];
        for (int i = 0; i < input.length; i++) {
            // Stabilité numérique
            if (input[i] >= 0) {
                double exp = Math.exp(-input[i]);
                output[i] = 1 / (1 + exp);
            } else {
                double exp = Math.exp(input[i]);
                output[i] = exp / (1 + exp);
            }
        }
        return output;
    }
    
    /**
     * Dérivée : σ'(x) = σ(x) * (1 - σ(x))
     */
    public static double[] derivative(double[] activated) {
        double[] grad = new double[activated.length];
        for (int i = 0; i < activated.length; i++) {
            grad[i] = activated[i] * (1 - activated[i]);
        }
        return grad;
    }
}

/**
 * Fonction softmax : σ_i(z) = e^(z_i) / sum(e^(z_j))
 */
public class Softmax {
    public static double[] activate(double[] logits) {
        // Stabilité numérique : soustraire max
        double max = java.util.Arrays.stream(logits).max().orElse(0);
        
        double[] exp = new double[logits.length];
        double sum = 0;
        
        for (int i = 0; i < logits.length; i++) {
            exp[i] = Math.exp(logits[i] - max);
            sum += exp[i];
        }
        
        double[] probs = new double[logits.length];
        for (int i = 0; i < logits.length; i++) {
            probs[i] = exp[i] / sum;
        }
        return probs;
    }
    
    /**
     * Dérivée Jacobienne : σ'_ij = σ_i * (δ_ij - σ_j)
     */
    public static double[][] derivative(double[] probs) {
        int n = probs.length;
        double[][] jacobian = new double[n][n];
        
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i == j) {
                    jacobian[i][j] = probs[i] * (1 - probs[i]);
                } else {
                    jacobian[i][j] = -probs[i] * probs[j];
                }
            }
        }
        return jacobian;
    }
}
```

---

## 7.3 Loss Functions

```java
/**
 * Cross-Entropy Loss pour classification multi-classe
 * L = -sum(y_i * log(pred_i))
 */
public class CrossEntropyLoss {
    
    /**
     * @param predictions probabilités softmax (sum = 1)
     * @param targets one-hot encoded labels
     * @return loss scalar
     */
    public static double compute(double[] predictions, double[] targets) {
        double loss = 0;
        double epsilon = 1e-7;  // Stabilité numérique
        
        for (int i = 0; i < targets.length; i++) {
            if (targets[i] == 1) {
                loss -= Math.log(predictions[i] + epsilon);
            }
        }
        return loss;
    }
    
    /**
     * Gradient de cross-entropy avec softmax
     * C'est BEAUCOUP plus simple que dériver la softmax seule !
     * dL/dz = predictions - targets
     */
    public static double[] gradient(double[] predictions, double[] targets) {
        double[] grad = new double[predictions.length];
        for (int i = 0; i < predictions.length; i++) {
            grad[i] = predictions[i] - targets[i];
        }
        return grad;
    }
    
    /**
     * Backward pass avec softmax (combiné pour stabilité)
     */
    public static double[] softmaxCrossEntropyGradient(double[] logits, double[] targets) {
        // Le résultat est juste : softmax(logits) - targets
        double[] probs = Softmax.activate(logits);
        return gradient(probs, targets);
    }
}

/**
 * Mean Squared Error : MSE = 1/n * sum((pred - target)^2)
 */
public class MSELoss {
    public static double compute(double[] predictions, double[] targets) {
        double sum = 0;
        for (int i = 0; i < predictions.length; i++) {
            double diff = predictions[i] - targets[i];
            sum += diff * diff;
        }
        return sum / predictions.length;
    }
    
    /**
     * Gradient : dL/dpred = 2/n * (pred - target)
     */
    public static double[] gradient(double[] predictions, double[] targets) {
        double[] grad = new double[predictions.length];
        double scale = 2.0 / predictions.length;
        for (int i = 0; i < predictions.length; i++) {
            grad[i] = scale * (predictions[i] - targets[i]);
        }
        return grad;
    }
}
```

---

## 7.4 Attention Mechanism Basique

```java
/**
 * Implémentation de scaled dot-product attention
 * Attention(Q,K,V) = softmax(Q*K^T / sqrt(d_k)) * V
 */
public class AttentionLayer {
    private int seqLen;
    private int d_k;  // dimension clé
    private int d_v;  // dimension valeur
    
    public AttentionLayer(int seqLen, int d_k, int d_v) {
        this.seqLen = seqLen;
        this.d_k = d_k;
        this.d_v = d_v;
    }
    
    /**
     * @param Q : queries, shape (seqLen, d_k)
     * @param K : keys, shape (seqLen, d_k)
     * @param V : values, shape (seqLen, d_v)
     * @return attention output, shape (seqLen, d_v)
     */
    public double[][] forward(double[][] Q, double[][] K, double[][] V) {
        // Étape 1 : Calculer scores = Q * K^T
        double[][] scores = matrixMultiply(Q, transpose(K));
        // shape : (seqLen, seqLen)
        
        // Étape 2 : Scaler par sqrt(d_k)
        double scale = Math.sqrt(d_k);
        for (int i = 0; i < seqLen; i++) {
            for (int j = 0; j < seqLen; j++) {
                scores[i][j] /= scale;
            }
        }
        
        // Étape 3 : Appliquer softmax par ligne
        double[][] weights = new double[seqLen][seqLen];
        for (int i = 0; i < seqLen; i++) {
            weights[i] = Softmax.activate(scores[i]);
        }
        
        // Étape 4 : Pondérer les values
        double[][] output = matrixMultiply(weights, V);
        // shape : (seqLen, d_v)
        
        return output;
    }
    
    // Utilitaires
    private double[][] matrixMultiply(double[][] A, double[][] B) {
        int m = A.length;
        int n = A[0].length;
        int p = B[0].length;
        double[][] C = new double[m][p];
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < p; j++) {
                for (int k = 0; k < n; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }
        return C;
    }
    
    private double[][] transpose(double[][] A) {
        int m = A.length;
        int n = A[0].length;
        double[][] T = new double[n][m];
        
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                T[j][i] = A[i][j];
            }
        }
        return T;
    }
}
```

---

# SECTION 8 : INTÉGRATION ANGULAR (FRONTEND)

## 8.1 Visualiseur d'Attention en Angular

```typescript
// attention-visualizer.component.ts
import { Component, OnInit } from '@angular/core';
import * as tf from '@tensorflow/tfjs';

interface AttentionVisualization {
  queries: tf.Tensor2D;
  keys: tf.Tensor2D;
  values: tf.Tensor2D;
  attentionWeights: tf.Tensor2D;
  output: tf.Tensor2D;
}

@Component({
  selector: 'app-attention-visualizer',
  templateUrl: './attention-visualizer.component.html',
  styleUrls: ['./attention-visualizer.component.css']
})
export class AttentionVisualizerComponent implements OnInit {
  seqLen = 5;
  d_k = 64;
  d_v = 64;
  
  visualization: AttentionVisualization | null = null;
  
  ngOnInit() {
    this.computeAttention();
  }
  
  /**
   * Implémente Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V
   */
  computeAttention() {
    // Créer Q, K, V aléatoires (dans un vrai modèle, ce sont les sorties précédentes)
    const Q = tf.randomNormal([this.seqLen, this.d_k]);
    const K = tf.randomNormal([this.seqLen, this.d_k]);
    const V = tf.randomNormal([this.seqLen, this.d_v]);
    
    // Étape 1 : scores = Q * K^T / sqrt(d_k)
    const scores = tf.tidy(() => {
      const dotProduct = tf.matMul(Q, K.transpose([1, 0]));
      const scale = Math.sqrt(this.d_k);
      return dotProduct.div(tf.scalar(scale));
    });
    
    // Étape 2 : appliquer softmax par ligne
    const attentionWeights = tf.tidy(() => {
      return tf.softmax(scores, 1);
    });
    
    // Étape 3 : output = attention_weights * V
    const output = tf.tidy(() => {
      return tf.matMul(attentionWeights, V);
    });
    
    this.visualization = {
      queries: Q as tf.Tensor2D,
      keys: K as tf.Tensor2D,
      values: V as tf.Tensor2D,
      attentionWeights: attentionWeights as tf.Tensor2D,
      output: output as tf.Tensor2D
    };
  }
  
  /**
   * Crée une heatmap CSS des poids d'attention
   */
  getAttentionHeatmap() {
    if (!this.visualization) return [];
    
    const data = this.visualization.attentionWeights.dataSync();
    const heatmap = [];
    
    for (let i = 0; i < this.seqLen; i++) {
      const row = [];
      for (let j = 0; j < this.seqLen; j++) {
        const intensity = data[i * this.seqLen + j];
        row.push({
          value: intensity.toFixed(3),
          color: `rgba(255, ${Math.floor(255 * (1 - intensity))}, 0, 0.7)`
        });
      }
      heatmap.push(row);
    }
    return heatmap;
  }
  
  /**
   * Simule l'ajustement d'un token en entrée et recalcule attention
   */
  updateTokenEmbedding(tokenIndex: number, deltaSize: number) {
    // Simuler une modification du token embedding
    tf.tidy(() => {
      if (this.visualization) {
        const newQ = this.visualization.queries.clone();
        const updates = tf.randomNormal([1, this.d_k]).mul(tf.scalar(deltaSize));
        // Note: tf.tensorScatterUpdate pour modification réelle
      }
    });
    this.computeAttention();
  }
  
  ngOnDestroy() {
    // Nettoyer les tensors
    if (this.visualization) {
      this.visualization.queries.dispose();
      this.visualization.keys.dispose();
      this.visualization.values.dispose();
      this.visualization.attentionWeights.dispose();
      this.visualization.output.dispose();
    }
  }
}
```

---

## 8.2 Template Angular pour Visualisation

```html
<!-- attention-visualizer.component.html -->
<div class="attention-container">
  <h2>Scaled Dot-Product Attention Visualizer</h2>
  
  <div class="controls">
    <label>
      Sequence Length: 
      <input type="number" [(ngModel)]="seqLen" (change)="computeAttention()" 
             min="2" max="16">
    </label>
    <label>
      Key Dimension: 
      <input type="number" [(ngModel)]="d_k" (change)="computeAttention()" 
             min="16" max="512" step="16">
    </label>
  </div>
  
  <div class="visualization" *ngIf="visualization">
    <div class="heatmap-section">
      <h3>Attention Weights Heatmap</h3>
      <div class="heatmap">
        <div *ngFor="let row of getAttentionHeatmap()" class="row">
          <div *ngFor="let cell of row" class="cell" 
               [style.background-color]="cell.color"
               [title]="'Weight: ' + cell.value">
            {{ cell.value }}
          </div>
        </div>
      </div>
      <p class="description">
        Matrice d'attention (seqLen × seqLen) : montre comment chaque token 
        (ligne) fait attention aux autres tokens (colonnes). 
        Plus clair = plus d'attention.
      </p>
    </div>
    
    <div class="formula-section">
      <h3>Formule Mathématique</h3>
      <code>
        Attention(Q,K,V) = softmax(Q·K<sup>T</sup>/√d<sub>k</sub>) · V
      </code>
      <ul class="parameters">
        <li>Q (Queries): {{ seqLen }} × {{ d_k }}</li>
        <li>K (Keys): {{ seqLen }} × {{ d_k }}</li>
        <li>V (Values): {{ seqLen }} × {{ d_v }}</li>
        <li>Output: {{ seqLen }} × {{ d_v }}</li>
      </ul>
    </div>
  </div>
</div>
```

---

## 8.3 Service Angular pour Calculs Mathématiques

```typescript
// math.service.ts
import { Injectable } from '@angular/core';
import * as tf from '@tensorflow/tfjs';

@Injectable({
  providedIn: 'root'
})
export class MathService {
  
  /**
   * Calcule la multiplication matricielle
   */
  matrixMultiply(A: number[][], B: number[][]): number[][] {
    const m = A.length;
    const n = A[0].length;
    const p = B[0].length;
    
    const C: number[][] = Array(m).fill(0).map(() => Array(p).fill(0));
    
    for (let i = 0; i < m; i++) {
      for (let j = 0; j < p; j++) {
        for (let k = 0; k < n; k++) {
          C[i][j] += A[i][k] * B[k][j];
        }
      }
    }
    return C;
  }
  
  /**
   * Calcule le gradient via chain rule
   * Pour f(g(x)), df/dx = df/dg * dg/dx
   */
  chainRuleGradient(
    outerGrad: number[],
    innerDerivative: (x: number[]) => number[][],
    input: number[]
  ): number[] {
    const jacobian = innerDerivative(input);
    const gradient = new Array(input.length).fill(0);
    
    for (let i = 0; i < input.length; i++) {
      for (let j = 0; j < outerGrad.length; j++) {
        gradient[i] += outerGrad[j] * jacobian[j][i];
      }
    }
    return gradient;
  }
  
  /**
   * Calcule la cross-entropy loss
   */
  crossEntropyLoss(predictions: number[], targets: number[]): number {
    let loss = 0;
    const epsilon = 1e-7;
    
    for (let i = 0; i < targets.length; i++) {
      if (targets[i] === 1) {
        loss -= Math.log(predictions[i] + epsilon);
      }
    }
    return loss;
  }
  
  /**
   * Calcule la norme L2 d'un vecteur
   */
  l2Norm(v: number[]): number {
    return Math.sqrt(v.reduce((sum, x) => sum + x * x, 0));
  }
  
  /**
   * Calcule le dot product de deux vecteurs
   */
  dotProduct(u: number[], v: number[]): number {
    return u.reduce((sum, u_i, i) => sum + u_i * v[i], 0);
  }
}
```

---

# SECTION 9 : ALGORITHMES DE COMPLEXITÉ

## 9.1 Analyse Empirique Temps/Espace

```java
/**
 * Benchmark de complexité algorithmique
 */
public class ComplexityBenchmark {
    
    /**
     * O(1) - Accès direct à tableau
     */
    public static long benchmarkConstant(int[] arr) {
        long start = System.nanoTime();
        int value = arr[500];  // Accès direct, toujours O(1)
        long end = System.nanoTime();
        return end - start;
    }
    
    /**
     * O(log n) - Recherche binaire
     */
    public static long benchmarkBinarySearch(int[] sortedArr, int target) {
        long start = System.nanoTime();
        int left = 0, right = sortedArr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (sortedArr[mid] == target) break;
            if (sortedArr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        long end = System.nanoTime();
        return end - start;
    }
    
    /**
     * O(n) - Parcours linéaire
     */
    public static long benchmarkLinear(int[] arr) {
        long start = System.nanoTime();
        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
        long end = System.nanoTime();
        return end - start;
    }
    
    /**
     * O(n log n) - Merge sort
     */
    public static long benchmarkMergeSort(int[] arr) {
        long start = System.nanoTime();
        mergeSort(arr, 0, arr.length - 1);
        long end = System.nanoTime();
        return end - start;
    }
    
    private static void mergeSort(int[] arr, int left, int right) {
        if (left < right) {
            int mid = left + (right - left) / 2;
            mergeSort(arr, left, mid);
            mergeSort(arr, mid + 1, right);
            merge(arr, left, mid, right);
        }
    }
    
    private static void merge(int[] arr, int left, int mid, int right) {
        int[] temp = new int[right - left + 1];
        int i = left, j = mid + 1, k = 0;
        
        while (i <= mid && j <= right) {
            temp[k++] = arr[i] <= arr[j] ? arr[i++] : arr[j++];
        }
        while (i <= mid) temp[k++] = arr[i++];
        while (j <= right) temp[k++] = arr[j++];
        
        for (i = left, k = 0; i <= right; i++, k++) {
            arr[i] = temp[k];
        }
    }
    
    /**
     * O(n²) - Bubble sort
     */
    public static long benchmarkBubbleSort(int[] arr) {
        long start = System.nanoTime();
        for (int i = 0; i < arr.length; i++) {
            for (int j = 0; j < arr.length - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
        long end = System.nanoTime();
        return end - start;
    }
    
    /**
     * Compare toutes les complexités
     */
    public static void main(String[] args) {
        int[] sizes = {100, 1000, 10000, 100000};
        
        for (int n : sizes) {
            int[] arr = new int[n];
            for (int i = 0; i < n; i++) {
                arr[i] = (int) (Math.random() * n);
            }
            
            System.out.println("\n--- Taille : " + n + " ---");
            System.out.println("O(1) Constant: " + benchmarkConstant(arr) + " ns");
            System.out.println("O(log n) Binary Search: " + benchmarkBinarySearch(arr, arr[0]) + " ns");
            System.out.println("O(n) Linear: " + benchmarkLinear(arr) + " ns");
            System.out.println("O(n log n) Merge Sort: " + benchmarkMergeSort(arr) + " ns");
            
            // Bubble sort seulement pour petites tailles
            if (n <= 10000) {
                int[] arrCopy = arr.clone();
                System.out.println("O(n²) Bubble Sort: " + benchmarkBubbleSort(arrCopy) + " ns");
            }
        }
    }
}
```

---

## 9.2 Arbre Binaire de Recherche

```java
/**
 * BST équilibré avec analyse de complexité
 */
public class BSTNode {
    int value;
    BSTNode left, right;
    int height = 1;  // Pour balancing (AVL)
    
    BSTNode(int value) {
        this.value = value;
    }
}

public class BalancedBST {
    private BSTNode root;
    
    /**
     * Insert - O(log n) si équilibré
     */
    public void insert(int value) {
        root = insertNode(root, value);
    }
    
    private BSTNode insertNode(BSTNode node, int value) {
        if (node == null) {
            return new BSTNode(value);
        }
        
        if (value < node.value) {
            node.left = insertNode(node.left, value);
        } else if (value > node.value) {
            node.right = insertNode(node.right, value);
        }
        
        updateHeight(node);
        return balance(node);
    }
    
    /**
     * Search - O(log n) si équilibré
     */
    public boolean search(int value) {
        return searchNode(root, value);
    }
    
    private boolean searchNode(BSTNode node, int value) {
        if (node == null) {
            return false;
        }
        
        if (value == node.value) {
            return true;
        } else if (value < node.value) {
            return searchNode(node.left, value);
        } else {
            return searchNode(node.right, value);
        }
    }
    
    /**
     * AVL rebalancing
     */
    private BSTNode balance(BSTNode node) {
        int balance = getBalance(node);
        
        // Left Heavy
        if (balance > 1) {
            if (getBalance(node.left) < 0) {
                node.left = rotateLeft(node.left);
            }
            return rotateRight(node);
        }
        
        // Right Heavy
        if (balance < -1) {
            if (getBalance(node.right) > 0) {
                node.right = rotateRight(node.right);
            }
            return rotateLeft(node);
        }
        
        return node;
    }
    
    private BSTNode rotateRight(BSTNode y) {
        BSTNode x = y.left;
        BSTNode T2 = x.right;
        
        x.right = y;
        y.left = T2;
        
        updateHeight(y);
        updateHeight(x);
        
        return x;
    }
    
    private BSTNode rotateLeft(BSTNode x) {
        BSTNode y = x.right;
        BSTNode T2 = y.left;
        
        y.left = x;
        x.right = T2;
        
        updateHeight(x);
        updateHeight(y);
        
        return y;
    }
    
    private int getBalance(BSTNode node) {
        if (node == null) return 0;
        return getHeight(node.left) - getHeight(node.right);
    }
    
    private int getHeight(BSTNode node) {
        return node == null ? 0 : node.height;
    }
    
    private void updateHeight(BSTNode node) {
        node.height = 1 + Math.max(getHeight(node.left), getHeight(node.right));
    }
    
    /**
     * Affiche le depth pour visualiser l'équilibre
     */
    public int getDepth() {
        return getHeight(root);
    }
}
```

---

# CONCLUSION & RESSOURCES

## Points Clés Retenus

1. **Algèbre Linéaire** : Tout est multiplication matricielle
2. **Gradients** : Chain rule + descente de gradient = entraînement
3. **Softmax + Cross-Entropy** : Standard de facto pour classification
4. **Attention** : Cœur des transformers modernes
5. **Complexité** : O(n²) attention limite les longueurs de séquence

## Pour Approfondir

```
Mathématiques ↔ Implémentation ↔ Application

         ↓
    
Théorèmes   → Code Java    → Modèles LLMs
(Papier)    (Déterministe) (Parallelisés)
```

## Prochaines Étapes

1. **Lire les papers originaux** :
   - "Attention Is All You Need" (2017)
   - "An Introduction to Statistical Learning"
   
2. **Implémenter depuis zéro** :
   - Petit transformer sur données synthétiques
   - Mesurer la complexité empiriquement
   
3. **Intégrer en production** :
   - ONNX Runtime pour inférence efficace
   - TensorFlow Lite pour edge devices

---

**Document créé pour développeurs Java/Angular ayant besoin de fondamentaux mathématiques des LLMs.**
