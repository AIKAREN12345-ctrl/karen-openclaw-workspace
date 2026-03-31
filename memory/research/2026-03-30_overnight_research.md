# Comprehensive Technical Architecture Research: Personal Productivity Dashboard with AI Integration

**Date:** 2026-03-30  
**Research Focus:** Technical architecture for a personal productivity dashboard with AI integration  
**Scope:** 10 focus areas covering database sync, AI frameworks, real-time collaboration, mobile strategies, voice interfaces, accessibility, security, performance, and analytics

---

## Table of Contents

1. [Database Sync Architecture](#1-database-sync-architecture)
2. [AI Agent Frameworks](#2-ai-agent-frameworks)
3. [Plugin/Widget System Architecture](#3-pluginwidget-system-architecture)
4. [Real-Time Collaboration](#4-real-time-collaboration)
5. [Mobile App Strategies](#5-mobile-app-strategies)
6. [Voice Interface Integration](#6-voice-interface-integration)
7. [Accessibility Best Practices](#7-accessibility-best-practices)
8. [Security Architecture](#8-security-architecture)
9. [Performance Optimization](#9-performance-optimization)
10. [Analytics & Insights](#10-analytics--insights)

---

## 1. Database Sync Architecture

### 1.1 SQLite to IndexedDB Synchronization Patterns

#### Core Approaches

**1. Electric SQL (Recommended)**
Electric SQL is a Postgres sync engine that handles partial replication, data delivery, and fan-out. While designed for Postgres, its architecture principles apply to SQLite sync:

```typescript
// Electric SQL-style sync pattern
import { useShape } from '@electric-sql/react'

function TaskList() {
  const { data } = useShape({
    url: `http://localhost:3000/v1/shape`,
    params: {
      table: `tasks`,
      where: `user_id = 'current_user'`,
    },
  })
  return <TaskListView tasks={data} />
}
```

**2. RxDB (Offline-First Database)**
RxDB implements the CouchDB replication protocol for client-side databases:

```typescript
import { createRxDatabase } from 'rxdb';
import { getRxStorageDexie } from 'rxdb/plugins/storage-dexie';

const db = await createRxDatabase({
  name: 'productivity_db',
  storage: getRxStorageDexie()
});

// Replication with CouchDB-compatible server
const replicationState = db.tasks.syncCouchDB({
  remote: 'http://localhost:5984/tasks',
  waitForLeadership: true,
  direction: {
    pull: true,
    push: true
  }
});
```

**3. Custom SQLite → IndexedDB Bridge**

```typescript
class SQLiteIndexedDBBridge {
  private sqlite: SQLiteDatabase;
  private indexedDB: IDBDatabase;
  private syncQueue: SyncOperation[] = [];

  async syncToIndexedDB() {
    const changes = await this.sqlite.getChangesSince(this.lastSyncTime);
    
    for (const change of changes) {
      await this.applyToIndexedDB(change);
    }
    
    this.lastSyncTime = Date.now();
  }

  async applyToIndexedDB(change: ChangeOperation) {
    const tx = this.indexedDB.transaction(['tasks'], 'readwrite');
    const store = tx.objectStore('tasks');
    
    switch (change.type) {
      case 'INSERT':
        await store.add(change.data);
        break;
      case 'UPDATE':
        await store.put(change.data);
        break;
      case 'DELETE':
        await store.delete(change.id);
        break;
    }
  }
}
```

### 1.2 Offline-First Data Strategies

#### Strategy 1: Local-First Architecture
- **Principle:** Data lives primarily on the device; sync is secondary
- **Benefits:** Fast reads/writes, works offline, user owns data
- **Implementation:**
  - Use IndexedDB as primary storage
  - Background sync to server when online
  - Conflict resolution on sync

#### Strategy 2: Optimistic UI with Rollback
```typescript
class OptimisticStore {
  async updateTask(taskId: string, updates: Partial<Task>) {
    // 1. Apply optimistically
    const previousState = this.cache.get(taskId);
    this.cache.set(taskId, { ...previousState, ...updates });
    this.notifySubscribers();

    try {
      // 2. Attempt server update
      await this.api.updateTask(taskId, updates);
    } catch (error) {
      // 3. Rollback on failure
      this.cache.set(taskId, previousState);
      this.notifySubscribers();
      throw error;
    }
  }
}
```

#### Strategy 3: Conflict-Free Replicated Data Types (CRDTs)
See Section 4 for detailed CRDT implementation.

### 1.3 Conflict Resolution for Multi-Device Sync

#### Last-Write-Wins (LWW) with Vector Clocks
```typescript
interface VectorClock {
  [deviceId: string]: number;
}

interface VersionedDocument {
  id: string;
  data: any;
  vectorClock: VectorClock;
  timestamp: number;
  deviceId: string;
}

function resolveConflict(
  local: VersionedDocument,
  remote: VersionedDocument
): VersionedDocument {
  const comparison = compareVectorClocks(local.vectorClock, remote.vectorClock);
  
  if (comparison === 1) return local;  // Local is newer
  if (comparison === -1) return remote; // Remote is newer
  
  // Concurrent edits - merge
  return mergeDocuments(local, remote);
}

function compareVectorClocks(a: VectorClock, b: VectorClock): number {
  let aGreater = false;
  let bGreater = false;
  
  const allKeys = new Set([...Object.keys(a), ...Object.keys(b)]);
  
  for (const key of allKeys) {
    const aVal = a[key] || 0;
    const bVal = b[key] || 0;
    
    if (aVal > bVal) aGreater = true;
    if (bVal > aVal) bGreater = true;
  }
  
  if (aGreater && !bGreater) return 1;
  if (bGreater && !aGreater) return -1;
  return 0; // Concurrent
}
```

#### Operational Transformation (OT)
See Section 4.3 for OT implementation details.

### 1.4 Real-Time Sync with WebSockets

#### Architecture Pattern
```typescript
class RealTimeSyncManager {
  private ws: WebSocket;
  private pendingChanges: Change[] = [];
  private syncState: 'connected' | 'disconnected' | 'syncing' = 'disconnected';

  constructor(private url: string) {
    this.connect();
  }

  private connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      this.syncState = 'connected';
      this.flushPendingChanges();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleServerMessage(message);
    };

    this.ws.onclose = () => {
      this.syncState = 'disconnected';
      setTimeout(() => this.connect(), 5000); // Reconnect
    };
  }

  async applyChange(change: Change) {
    if (this.syncState === 'connected') {
      this.ws.send(JSON.stringify({
        type: 'CHANGE',
        payload: change
      }));
    } else {
      this.pendingChanges.push(change);
      await this.queueForSync(change);
    }
  }

  private async flushPendingChanges() {
    for (const change of this.pendingChanges) {
      this.ws.send(JSON.stringify({
        type: 'CHANGE',
        payload: change
      }));
    }
    this.pendingChanges = [];
  }
}
```

#### Recommended Stack
- **Client:** rxdb (IndexedDB storage) + yjs (CRDTs)
- **Server:** Hocuspocus (Yjs WebSocket server) or custom Node.js with Socket.io
- **Protocol:** Yjs binary protocol for efficiency

---

## 2. AI Agent Frameworks

### 2.1 Multi-Agent Orchestration Patterns

#### Pattern 1: Orchestrator-Workers (Anthropic Recommended)
```typescript
interface Agent {
  name: string;
  systemPrompt: string;
  tools: Tool[];
}

class OrchestratorAgent {
  private agents: Map<string, Agent> = new Map();

  async executeTask(task: string): Promise<string> {
    // Step 1: Plan decomposition
    const plan = await this.llm.generate({
      prompt: `Break down this task into subtasks: ${task}`,
      outputSchema: z.array(z.object({
        agent: z.string(),
        subtask: z.string()
      }))
    });

    // Step 2: Delegate to workers
    const results = await Promise.all(
      plan.map(async (step) => {
        const agent = this.agents.get(step.agent);
        return this.executeSubtask(agent, step.subtask);
      })
    );

    // Step 3: Synthesize results
    return this.synthesizeResults(results);
  }
}
```

#### Pattern 2: Routing Pattern
```typescript
class RouterAgent {
  private specializedAgents: Map<string, Agent> = new Map();

  async route(input: string): Promise<string> {
    const classification = await this.llm.classify(input, [
      'task_management',
      'calendar_scheduling',
      'note_taking',
      'analytics'
    ]);

    const agent = this.specializedAgents.get(classification);
    return agent.execute(input);
  }
}
```

#### Pattern 3: Evaluator-Optimizer Loop
```typescript
class EvaluatorOptimizerAgent {
  async executeWithRefinement(task: string, maxIterations = 3): Promise<string> {
    let result = await this.generator.generate(task);
    
    for (let i = 0; i < maxIterations; i++) {
      const evaluation = await this.evaluator.evaluate(result, task);
      
      if (evaluation.score >= 0.9) break;
      
      result = await this.generator.refine(result, evaluation.feedback);
    }
    
    return result;
  }
}
```

### 2.2 Context Window Management Strategies

#### Strategy 1: Sliding Window with Summarization
```typescript
class ContextWindowManager {
  private maxTokens = 128000;
  private messages: Message[] = [];

  async addMessage(message: Message) {
    this.messages.push(message);
    
    const tokenCount = await this.countTokens(this.messages);
    
    if (tokenCount > this.maxTokens * 0.8) {
      await this.compressHistory();
    }
  }

  private async compressHistory() {
    // Summarize oldest messages
    const toSummarize = this.messages.slice(0, this.messages.length / 2);
    const summary = await this.llm.summarize(toSummarize);
    
    this.messages = [
      { role: 'system', content: `Previous context: ${summary}` },
      ...this.messages.slice(this.messages.length / 2)
    ];
  }
}
```

#### Strategy 2: Hierarchical Context
```typescript
interface HierarchicalContext {
  immediate: Message[];      // Last 10 messages
  session: string;           // Session summary
  longTerm: string[];        // Key facts/relationships
}

class HierarchicalContextManager {
  async buildContext(userId: string): Promise<HierarchicalContext> {
    const immediate = await this.getRecentMessages(userId, 10);
    const session = await this.getOrCreateSessionSummary(userId);
    const longTerm = await this.retrieveRelevantFacts(userId, immediate);
    
    return { immediate, session, longTerm };
  }
}
```

### 2.3 RAG (Retrieval-Augmented Generation) Implementation

#### Vector Search Architecture
```typescript
class RAGSystem {
  private embeddingModel: EmbeddingModel;
  private vectorStore: VectorStore;

  async indexDocument(doc: Document) {
    const chunks = this.chunkDocument(doc);
    
    for (const chunk of chunks) {
      const embedding = await this.embeddingModel.embed(chunk.text);
      await this.vectorStore.upsert({
        id: `${doc.id}-${chunk.index}`,
        embedding,
        metadata: {
          docId: doc.id,
          chunkIndex: chunk.index,
          text: chunk.text
        }
      });
    }
  }

  async query(question: string, topK = 5): Promise<string> {
    const queryEmbedding = await this.embeddingModel.embed(question);
    const results = await this.vectorStore.similaritySearch(queryEmbedding, topK);
    
    const context = results.map(r => r.metadata.text).join('\n\n');
    
    return this.llm.generate({
      prompt: `Answer based on context:\n${context}\n\nQuestion: ${question}`,
      system: 'You are a helpful assistant. Answer based only on the provided context.'
    });
  }

  private chunkDocument(doc: Document): Chunk[] {
    // Semantic chunking with overlap
    const chunks: Chunk[] = [];
    const chunkSize = 512;
    const overlap = 50;
    
    for (let i = 0; i < doc.text.length; i += chunkSize - overlap) {
      chunks.push({
        index: chunks.length,
        text: doc.text.slice(i, i + chunkSize)
      });
    }
    
    return chunks;
  }
}
```

#### Hybrid Search (Vector + Full-Text)
```typescript
async function hybridSearch(query: string) {
  // Parallel vector and full-text search
  const [vectorResults, textResults] = await Promise.all([
    vectorStore.similaritySearch(query, 10),
    fullTextSearch(query, 10)
  ]);

  // Reciprocal Rank Fusion
  const scores = new Map<string, number>();
  const k = 60;

  // Score vector results
  vectorResults.forEach((result, rank) => {
    const current = scores.get(result.id) || 0;
    scores.set(result.id, current + 1 / (k + rank + 1));
  });

  // Score text results
  textResults.forEach((result, rank) => {
    const current = scores.get(result.id) || 0;
    scores.set(result.id, current + 1 / (k + rank + 1));
  });

  // Return sorted by fused score
  return Array.from(scores.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);
}
```

### 2.4 AI-Powered Task Prioritization Algorithms

#### Eisenhower Matrix with AI
```typescript
interface Task {
  id: string;
  title: string;
  description: string;
  deadline?: Date;
  estimatedDuration: number;
  tags: string[];
}

interface PrioritizedTask extends Task {
  urgency: number;      // 0-1
  importance: number;   // 0-1
  priorityScore: number;
  quadrant: 'urgent-important' | 'not-urgent-important' | 
            'urgent-not-important' | 'not-urgent-not-important';
}

class AIPrioritizer {
  async prioritize(tasks: Task[]): Promise<PrioritizedTask[]> {
    const prioritized = await Promise.all(
      tasks.map(async (task) => {
        const analysis = await this.llm.generate({
          prompt: `Analyze this task for urgency and importance:\n${JSON.stringify(task)}`,
          outputSchema: z.object({
            urgency: z.number().min(0).max(1),
            importance: z.number().min(0).max(1),
            reasoning: z.string()
          })
        });

        return {
          ...task,
          ...analysis,
          priorityScore: this.calculatePriorityScore(analysis),
          quadrant: this.determineQuadrant(analysis)
        };
      })
    );

    return prioritized.sort((a, b) => b.priorityScore - a.priorityScore);
  }

  private calculatePriorityScore(analysis: { urgency: number; importance: number }): number {
    // Weighted scoring: importance slightly higher than urgency
    return analysis.importance * 0.6 + analysis.urgency * 0.4;
  }
}
```

#### Time-Aware Scheduling Algorithm
```typescript
class SmartScheduler {
  async scheduleTasks(tasks: Task[], availableSlots: TimeSlot[]): Promise<ScheduledTask[]> {
    const prioritized = await this.prioritizer.prioritize(tasks);
    const scheduled: ScheduledTask[] = [];

    for (const task of prioritized) {
      const bestSlot = this.findOptimalSlot(task, availableSlots, scheduled);
      
      if (bestSlot) {
        scheduled.push({
          ...task,
          scheduledStart: bestSlot.start,
          scheduledEnd: new Date(bestSlot.start.getTime() + task.estimatedDuration * 60000)
        });
        
        // Remove used slot
        availableSlots = this.removeSlot(availableSlots, bestSlot, task.estimatedDuration);
      }
    }

    return scheduled;
  }

  private findOptimalSlot(
    task: Task, 
    slots: TimeSlot[], 
    alreadyScheduled: ScheduledTask[]
  ): TimeSlot | null {
    // Consider energy levels, deadlines, and context switching
    return slots
      .filter(slot => this.slotFitsTask(slot, task))
      .sort((a, b) => this.scoreSlot(b, task, alreadyScheduled) - 
                     this.scoreSlot(a, task, alreadyScheduled))[0] || null;
  }
}
```

---

## 3. Plugin/Widget System Architecture

### 3.1 Dynamic Widget Loading

#### Module Federation (Micro-Frontends)
```typescript
// Widget Host
class WidgetHost {
  private widgetRegistry: Map<string, WidgetManifest> = new Map();

  async loadWidget(widgetId: string): Promise<React.ComponentType> {
    const manifest = this.widgetRegistry.get(widgetId);
    
    if (!manifest) {
      // Fetch from remote
      const remoteEntry = await import(/* webpackIgnore: true */ manifest.url);
      await remoteEntry.init(__webpack_share_scopes__.default);
      
      const factory = await remoteEntry.get('./Widget');
      return factory();
    }
    
    return manifest.component;
  }
}

// Widget Manifest
interface WidgetManifest {
  id: string;
  name: string;
  version: string;
  url: string;           // Remote entry URL
  permissions: string[];
  apiVersion: string;
}
```

#### Iframe-Based Sandboxing
```typescript
class IframeWidgetContainer {
  private iframe: HTMLIFrameElement;

  constructor(private manifest: WidgetManifest) {
    this.iframe = document.createElement('iframe');
    this.iframe.sandbox = 'allow-scripts allow-same-origin';
    this.iframe.src = manifest.url;
    
    this.setupMessageChannel();
  }

  private setupMessageChannel() {
    const channel = new MessageChannel();
    
    channel.port1.onmessage = (event) => {
      this.handleWidgetMessage(event.data);
    };
    
    this.iframe.onload = () => {
      this.iframe.contentWindow?.postMessage(
        { type: 'INIT', apiVersion: this.manifest.apiVersion },
        '*',
        [channel.port2]
      );
    };
  }

  private handleWidgetMessage(message: WidgetMessage) {
    // Validate and route messages
    if (this.validateMessage(message)) {
      this.executeWidgetAction(message);
    }
  }
}
```

### 3.2 Plugin Marketplace Architecture

#### Plugin Registry
```typescript
interface PluginPackage {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  permissions: Permission[];
  entryPoint: string;
  icon: string;
  screenshots: string[];
  rating: number;
  downloadCount: number;
}

class PluginMarketplace {
  async searchPlugins(query: string, filters: FilterOptions): Promise<PluginPackage[]> {
    return this.api.search({
      q: query,
      category: filters.category,
      minRating: filters.minRating,
      sortBy: filters.sortBy
    });
  }

  async installPlugin(pluginId: string): Promise<void> {
    const plugin = await this.api.getPlugin(pluginId);
    
    // Verify permissions
    const granted = await this.permissionManager.requestPermissions(plugin.permissions);
    
    if (!granted) {
      throw new Error('Permissions denied');
    }

    // Download and install
    await this.downloadPlugin(plugin);
    await this.registerPlugin(plugin);
  }
}
```

### 3.3 Widget API Design

#### TypeScript Widget API
```typescript
// Widget API exposed to plugins
interface DashboardAPI {
  // Data access
  data: {
    getTasks(filters?: TaskFilter): Promise<Task[]>;
    createTask(task: Partial<Task>): Promise<Task>;
    updateTask(id: string, updates: Partial<Task>): Promise<Task>;
    deleteTask(id: string): Promise<void>;
    
    subscribeToTasks(callback: (tasks: Task[]) => void): Unsubscribe;
  };

  // UI integration
  ui: {
    showNotification(message: string, options?: NotificationOptions): void;
    openModal(content: React.ReactNode): void;
    registerShortcut(key: string, handler: () => void): void;
  };

  // AI capabilities
  ai: {
    complete(prompt: string, options?: CompletionOptions): Promise<string>;
    embed(text: string): Promise<number[]>;
    classify(text: string, labels: string[]): Promise<string>;
  };

  // Storage (isolated per plugin)
  storage: {
    get<T>(key: string): Promise<T | null>;
    set<T>(key: string, value: T): Promise<void>;
    remove(key: string): Promise<void>;
  };
}

// Plugin entry point signature
type PluginEntry = (api: DashboardAPI, context: PluginContext) => PluginInstance;

interface PluginInstance {
  name: string;
  widgets: WidgetDefinition[];
  activate(): void;
  deactivate(): void;
}
```

### 3.4 Security Sandboxing for Third-Party Widgets

#### Content Security Policy
```typescript
// CSP for widget iframes
const widgetCSP = `
  default-src 'none';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  connect-src https://api.dashboard.com;
  img-src 'self' blob: data:;
  font-src 'self';
`;

class SecureWidgetContainer {
  createSandbox(): HTMLIFrameElement {
    const iframe = document.createElement('iframe');
    
    // Strict sandbox
    iframe.sandbox = [
      'allow-scripts',
      'allow-same-origin',
      // 'allow-popups',      // Optional
      // 'allow-forms',       // If needed
    ].join(' ');
    
    // CSP via meta tag in iframe
    const cspMeta = `<meta http-equiv="Content-Security-Policy" content="${widgetCSP}">`;
    
    return iframe;
  }
}
```

#### Permission System
```typescript
enum Permission {
  READ_TASKS = 'read:tasks',
  WRITE_TASKS = 'write:tasks',
  READ_CALENDAR = 'read:calendar',
  WRITE_CALENDAR = 'write:calendar',
  USE_AI = 'use:ai',
  NETWORK_REQUEST = 'network:request',
  STORAGE = 'storage'
}

class PermissionManager {
  async requestPermissions(permissions: Permission[]): Promise<boolean> {
    const granted = await this.showPermissionDialog(permissions);
    
    if (granted) {
      for (const permission of permissions) {
        await this.grantPermission(permission);
      }
    }
    
    return granted;
  }

  checkPermission(permission: Permission): boolean {
    return this.grantedPermissions.has(permission);
  }
}
```

---

## 4. Real-Time Collaboration

### 4.1 WebSocket Implementation Patterns

#### Scalable WebSocket Architecture
```typescript
// Using Socket.io for room-based collaboration
class CollaborationServer {
  private io: Server;
  private rooms: Map<string, RoomState> = new Map();

  constructor(server: HttpServer) {
    this.io = new Server(server, {
      cors: { origin: process.env.CLIENT_URL },
      transports: ['websocket', 'polling']
    });

    this.io.on('connection', (socket) => {
      this.handleConnection(socket);
    });
  }

  private handleConnection(socket: Socket) {
    socket.on('join-room', (roomId: string, userId: string) => {
      socket.join(roomId);
      
      const room = this.getOrCreateRoom(roomId);
      room.addParticipant(userId, socket.id);
      
      // Broadcast presence
      socket.to(roomId).emit('user-joined', {
        userId,
        timestamp: Date.now()
      });
      
      // Send current state to new participant
      socket.emit('room-state', room.getState());
    });

    socket.on('operation', (roomId: string, operation: Operation) => {
      const room = this.rooms.get(roomId);
      if (room) {
        room.applyOperation(operation);
        socket.to(roomId).emit('operation', operation);
      }
    });

    socket.on('cursor-move', (roomId: string, position: CursorPosition) => {
      socket.to(roomId).emit('cursor-move', {
        userId: socket.userId,
        position
      });
    });
  }
}
```

### 4.2 CRDTs (Conflict-free Replicated Data Types)

#### Yjs Implementation
```typescript
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

class CRDTDocument {
  private doc: Y.Doc;
  private provider: WebsocketProvider;
  private tasks: Y.Array<Y.Map<any>>;

  constructor(roomId: string) {
    this.doc = new Y.Doc();
    
    this.provider = new WebsocketProvider(
      'wss://collab.example.com',
      roomId,
      this.doc
    );

    this.tasks = this.doc.getArray('tasks');
    this.setupObservers();
  }

  private setupObservers() {
    this.tasks.observe((event) => {
      console.log('Tasks changed:', event.changes);
    });
  }

  addTask(task: Task) {
    const yTask = new Y.Map();
    yTask.set('id', task.id);
    yTask.set('title', task.title);
    yTask.set('completed', task.completed);
    yTask.set('createdAt', task.createdAt);
    
    this.tasks.push([yTask]);
  }

  updateTask(id: string, updates: Partial<Task>) {
    const yTask = this.findTask(id);
    if (yTask) {
      Object.entries(updates).forEach(([key, value]) => {
        yTask.set(key, value);
      });
    }
  }

  getTasks(): Task[] {
    return this.tasks.toArray().map(yTask => ({
      id: yTask.get('id'),
      title: yTask.get('title'),
      completed: yTask.get('completed'),
      createdAt: yTask.get('createdAt')
    }));
  }
}
```

#### Custom LWW-Register CRDT
```typescript
class LWWRegister<T> {
  private value: T | null = null;
  private timestamp: number = 0;
  private replicaId: string;

  constructor(replicaId: string) {
    this.replicaId = replicaId;
  }

  set(value: T) {
    this.value = value;
    this.timestamp = Date.now();
  }

  get(): T | null {
    return this.value;
  }

  merge(other: LWWRegister<T>): LWWRegister<T> {
    if (other.timestamp > this.timestamp) {
      return other;
    } else if (other.timestamp < this.timestamp) {
      return this;
    } else {
      // Tie-break by replica ID
      return other.replicaId > this.replicaId ? other : this;
    }
  }

  toJSON() {
    return {
      value: this.value,
      timestamp: this.timestamp,
      replicaId: this.replicaId
    };
  }
}
```

### 4.3 Operational Transformation

#### Text OT Implementation
```typescript
interface Operation {
  type: 'retain' | 'insert' | 'delete';
  count?: number;      // For retain/delete
  text?: string;       // For insert
}

type OTTransform = Operation[];

class OperationalTransformation {
  // Transform operation A against operation B
  static transform(a: OTTransform, b: OTTransform): [OTTransform, OTTransform] {
    const aPrime: OTTransform = [];
    const bPrime: OTTransform = [];
    
    let i = 0, j = 0;
    
    while (i < a.length && j < b.length) {
      const opA = a[i];
      const opB = b[j];
      
      if (opA.type === 'insert') {
        aPrime.push(opA);
        bPrime.push({ type: 'retain', count: opA.text!.length });
        i++;
      } else if (opB.type === 'insert') {
        aPrime.push({ type: 'retain', count: opB.text!.length });
        bPrime.push(opB);
        j++;
      } else if (opA.type === 'retain' && opB.type === 'retain') {
        const minCount = Math.min(opA.count!, opB.count!);
        aPrime.push({ type: 'retain', count: minCount });
        bPrime.push({ type: 'retain', count: minCount });
        
        if (opA.count! > minCount) a[i] = { ...opA, count: opA.count! - minCount };
        else i++;
        
        if (opB.count! > minCount) b[j] = { ...opB, count: opB.count! - minCount };
        else j++;
      }
      // Handle delete operations...
    }
    
    return [aPrime, bPrime];
  }

  static apply(doc: string, ops: OTTransform): string {
    let result = '';
    let index = 0;
    
    for (const op of ops) {
      switch (op.type) {
        case 'retain':
          result += doc.slice(index, index + op.count!);
          index += op.count!;
          break;
        case 'insert':
          result += op.text;
          break;
        case 'delete':
          index += op.count!;
          break;
      }
    }
    
    return result + doc.slice(index);
  }
}
```

### 4.4 Presence Awareness

```typescript
interface UserPresence {
  userId: string;
  name: string;
  avatar: string;
  cursor?: {
    x: number;
    y: number;
    elementId?: string;
  };
  selection?: {
    start: number;
    end: number;
  };
  lastSeen: number;
  status: 'active' | 'idle' | 'away';
}

class PresenceManager {
  private presence: Map<string, UserPresence> = new Map();
  private awareness: Awareness;  // Yjs awareness

  constructor(doc: Y.Doc) {
    this.awareness = new Awareness(doc);
    
    this.awareness.on('change', () => {
      this.updatePresence();
    });
  }

  setLocalPresence(presence: Partial<UserPresence>) {
    this.awareness.setLocalState({
      ...this.awareness.getLocalState(),
      ...presence,
      lastSeen: Date.now()
    });
  }

  getAllPresence(): UserPresence[] {
    return Array.from(this.awareness.getStates().values())
      .filter(state => state !== null) as UserPresence[];
  }

  private updatePresence() {
    const states = this.getAllPresence();
    // Notify UI components
    this.emit('presence-change', states);
  }
}
```

---

## 5. Mobile App Strategies

### 5.1 Capacitor vs React Native Comparison

| Feature | Capacitor | React Native |
|---------|-----------|--------------|
| **Architecture** | WebView-based (hybrid) | Native bridge (JS → Native) |
| **Performance** | Good for most apps | Better for complex animations |
| **Native Access** | Plugins + native bridges | Direct native module access |
| **Code Sharing** | 100% with web | ~70-90% with web |
| **Bundle Size** | Larger (WebView overhead) | Smaller, more efficient |
| **Hot Reload** | Web dev server | Fast Refresh |
| **Ecosystem** | Ionic ecosystem | Massive React Native ecosystem |
| **Learning Curve** | Low (web tech) | Medium (requires native knowledge) |
| **Best For** | Content apps, dashboards | Complex native apps, games |

### 5.2 Recommendation for Productivity Dashboard

**Capacitor is recommended** because:
1. Productivity dashboards are content-heavy, not animation-heavy
2. Maximum code sharing with web platform
3. Faster development iteration
4. Easier maintenance (single codebase)
5. Excellent plugin ecosystem for native features

### 5.3 Native Feature Access

#### Capacitor Implementation
```typescript
// capacitor.config.ts
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.productivity.dashboard',
  appName: 'Productivity Dashboard',
  webDir: 'dist',
  plugins: {
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert']
    },
    LocalNotifications: {
      smallIcon: 'ic_stat_icon_config_sample',
      iconColor: '#488AFF'
    }
  }
};

export default config;
```

#### Push Notifications
```typescript
import { PushNotifications } from '@capacitor/push-notifications';

class NotificationService {
  async initialize() {
    // Request permission
    const result = await PushNotifications.requestPermissions();
    
    if (result.receive === 'granted') {
      await PushNotifications.register();
    }

    // Listen for notifications
    PushNotifications.addListener('pushNotificationReceived', (notification) => {
      this.handleNotification(notification);
    });

    // Handle notification tap
    PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
      this.handleNotificationTap(action.notification);
    });
  }

  async scheduleTaskReminder(task: Task, minutesBefore: number = 15) {
    const { LocalNotifications } = await import('@capacitor/local-notifications');
    
    await LocalNotifications.schedule({
      notifications: [{
        id: task.id,
        title: 'Task Reminder',
        body: task.title,
        schedule: { at: new Date(task.dueDate.getTime() - minutesBefore * 60000) }
      }]
    });
  }
}
```

#### Camera Access
```typescript
import { Camera, CameraResultType } from '@capacitor/camera';

class CameraService {
  async captureImage(): Promise<string> {
    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: true,
      resultType: CameraResultType.Base64,
      source: 'prompt' // Camera or gallery
    });

    return image.base64String!;
  }
}
```

### 5.4 App Store Deployment

#### iOS Deployment Checklist
```bash
# Build production app
cd ios/App
xcodebuild -workspace App.xcworkspace -scheme App -configuration Release

# Archive and upload
xcodebuild -workspace App.xcworkspace -scheme App archive -archivePath build/App.xcarchive
xcodebuild -exportArchive -archivePath build/App.xcarchive -exportOptionsPlist exportOptions.plist -exportPath build/IPA

# Or use Transporter app for upload
```

#### Android Deployment
```bash
# Generate signed APK/Bundle
cd android
./gradlew bundleRelease

# Upload to Play Console
# app/build/outputs/bundle/release/app-release.aab
```

### 5.5 Performance Optimization

#### Lazy Loading Routes
```typescript
// React Router with lazy loading
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Tasks = lazy(() => import('./pages/Tasks'));
const Analytics = lazy(() => import('./pages/Analytics'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

#### Virtual Scrolling for Lists
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualTaskList({ tasks }: { tasks: Task[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: tasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 72, // Estimated row height
    overscan: 5
  });

  return (
    <div ref={parentRef} style={{ height: '100%', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`
            }}
          >
            <TaskItem task={tasks[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 6. Voice Interface Integration

### 6.1 Speech-to-Text APIs

#### OpenAI Whisper Integration
```typescript
import OpenAI from 'openai';

class WhisperSTT {
  private openai: OpenAI;

  constructor(apiKey: string) {
    this.openai = new OpenAI({ apiKey });
  }

  async transcribe(audioBlob: Blob): Promise<string> {
    const file = new File([audioBlob], 'audio.webm', { type: 'audio/webm' });
    
    const response = await this.openai.audio.transcriptions.create({
      file,
      model: 'whisper-1',
      language: 'en',
      response_format: 'text'
    });

    return response;
  }

  // Real-time streaming with WebSocket
  async transcribeStream(audioStream: MediaStream, onTranscript: (text: string) => void) {
    const mediaRecorder = new MediaRecorder(audioStream, {
      mimeType: 'audio/webm;codecs=opus'
    });

    const chunks: Blob[] = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.push(e.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: 'audio/webm' });
      const transcript = await this.transcribe(blob);
      onTranscript(transcript);
    };

    // Record in 3-second chunks for near real-time
    mediaRecorder.start(3000);

    return () => mediaRecorder.stop();
  }
}
```

#### Web Speech API (Browser Native)
```typescript
class WebSpeechSTT {
  private recognition: SpeechRecognition;

  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
  }

  start(onResult: (transcript: string, isFinal: boolean) => void) {
    this.recognition.onresult = (event) => {
      const results = event.results;
      const lastResult = results[results.length - 1];
      const transcript = lastResult[0].transcript;
      
      onResult(transcript, lastResult.isFinal);
    };

    this.recognition.start();
  }

  stop() {
    this.recognition.stop();
  }
}
```

### 6.2 Voice Command Processing

#### Intent Recognition
```typescript
interface VoiceCommand {
  intent: 'create_task' | 'complete_task' | 'schedule_event' | 'search' | 'unknown';
  entities: Record<string, any>;
  confidence: number;
}

class VoiceCommandProcessor {
  private llm: LLMClient;

  async processCommand(transcript: string): Promise<VoiceCommand> {
    const response = await this.llm.generate({
      prompt: `Parse this voice command: "${transcript}"`,
      system: `You are a voice command parser for a productivity app.
      Extract intent and entities from the user's command.
      
      Intents: create_task, complete_task, schedule_event, search, unknown
      
      Respond in JSON format:
      {
        "intent": "create_task",
        "entities": { "title": "Buy groceries", "dueDate": "tomorrow" },
        "confidence": 0.95
      }`,
      outputSchema: z.object({
        intent: z.enum(['create_task', 'complete_task', 'schedule_event', 'search', 'unknown']),
        entities: z.record(z.any()),
        confidence: z.number()
      })
    });

    return response;
  }

  async executeCommand(command: VoiceCommand): Promise<string> {
    switch (command.intent) {
      case 'create_task':
        return this.createTask(command.entities);
      case 'complete_task':
        return this.completeTask(command.entities);
      case 'schedule_event':
        return this.scheduleEvent(command.entities);
      case 'search':
        return this.search(command.entities);
      default:
        return "I'm not sure what you'd like me to do.";
    }
  }
}
```

### 6.3 Text-to-Speech for Responses

#### OpenAI TTS
```typescript
class OpenAITTS {
  private openai: OpenAI;

  async speak(text: string, voice: 'alloy' | 'echo' | 'fable' | 'onyx' | 'nova' | 'shimmer' = 'alloy') {
    const response = await this.openai.audio.speech.create({
      model: 'tts-1',
      voice,
      input: text,
      response_format: 'mp3'
    });

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    const audio = new Audio(url);
    await audio.play();
    
    return audio;
  }
}
```

#### Web Speech Synthesis (Browser Native)
```typescript
class WebSpeechTTS {
  speak(text: string, options?: SpeechSynthesisUtterance) {
    const utterance = new SpeechSynthesisUtterance(text);
    
    if (options) {
      Object.assign(utterance, options);
    }

    // Select a good voice
    const voices = speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.name.includes('Google')) || voices[0];
    utterance.voice = preferredVoice;

    speechSynthesis.speak(utterance);
  }

  stop() {
    speechSynthesis.cancel();
  }
}
```

### 6.4 Wake Word Detection

#### Porcupine Integration
```typescript
import { PorcupineWorker } from '@picovoice/porcupine-web';

class WakeWordDetector {
  private porcupine: PorcupineWorker | null = null;

  async initialize(accessKey: string, wakeWord: string) {
    this.porcupine = await PorcupineWorker.create(
      accessKey,
      [PorcupineWeb.BUILT_IN_KEYWORDS['Hey Google']],
      this.onWakeWord.bind(this)
    );
  }

  private onWakeWord(keywordIndex: number) {
    if (keywordIndex === 0) {
      this.emit('wake-word-detected');
    }
  }

  async start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    
    // Process audio through Porcupine
    // Implementation depends on Porcupine version
  }
}
```

---

## 7. Accessibility Best Practices

### 7.1 WCAG 2.1 Compliance

#### Key Requirements
- **Perceivable:** Text alternatives, captions, color contrast (4.5:1 for normal text)
- **Operable:** Keyboard accessible, enough time, no seizures, navigable
- **Understandable:** Readable, predictable, input assistance
- **Robust:** Compatible with assistive technologies

#### Implementation Checklist
```typescript
// ARIA labels and roles
<button 
  aria-label="Create new task"
  aria-pressed={isPressed}
  role="button"
>
  <PlusIcon />
</button>

// Focus management
<div 
  role="dialog" 
  aria-modal="true"
  aria-labelledby="dialog-title"
  tabIndex={-1}
  ref={dialogRef}
>
  <h2 id="dialog-title">Create Task</h2>
  {/* Dialog content */}
</div>

// Live regions for dynamic content
<div aria-live="polite" aria-atomic="true">
  {notification && <span>{notification.message}</span>}
</div>
```

### 7.2 Screen Reader Support

```typescript
// React hook for announcing to screen readers
function useAnnouncer() {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', priority);
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }, []);

  return { announce };
}

// Usage in component
function TaskList() {
  const { announce } = useAnnouncer();
  const tasks = useTasks();

  useEffect(() => {
    announce(`${tasks.length} tasks loaded`);
  }, [tasks.length]);

  return (
    <ul role="list" aria-label="Task list">
      {tasks.map(task => (
        <li key={task.id} role="listitem">
          <TaskItem task={task} />
        </li>
      ))}
    </ul>
  );
}
```

### 7.3 Keyboard Navigation

```typescript
// Focus trap for modals
function useFocusTrap(isActive: boolean) {
  const containerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!isActive) return;

    const container = containerRef.current;
    if (!container) return;

    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey && document.activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    };

    container.addEventListener('keydown', handleTabKey);
    firstElement?.focus();

    return () => container.removeEventListener('keydown', handleTabKey);
  }, [isActive]);

  return containerRef;
}

// Keyboard shortcuts
function useKeyboardShortcuts(shortcuts: Record<string, () => void>) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const key = `${e.ctrlKey || e.metaKey ? 'Ctrl+' : ''}${e.shiftKey ? 'Shift+' : ''}${e.key}`;
      
      if (shortcuts[key]) {
        e.preventDefault();
        shortcuts[key]();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [shortcuts]);
}
```

### 7.4 Color Contrast and Themes

```typescript
// CSS Custom Properties for theming
const themes = {
  light: {
    '--bg-primary': '#ffffff',
    '--bg-secondary': '#f5f5f5',
    '--text-primary': '#1a1a1a',
    '--text-secondary': '#666666',
    '--accent': '#0066cc',
    '--accent-contrast': '#ffffff',
    '--error': '#dc2626',
    '--success': '#16a34a'
  },
  dark: {
    '--bg-primary': '#1a1a1a',
    '--bg-secondary': '#2d2d2d',
    '--text-primary': '#ffffff',
    '--text-secondary': '#a0a0a0',
    '--accent': '#4d9fff',
    '--accent-contrast': '#000000',
    '--error': '#ef4444',
    '--success': '#22c55e'
  }
};

// Contrast ratio calculation
function getContrastRatio(color1: string, color2: string): number {
  const lum1 = getLuminance(color1);
  const lum2 = getLuminance(color2);
  
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  
  return (brightest + 0.05) / (darkest + 0.05);
}

function getLuminance(color: string): number {
  const rgb = hexToRgb(color);
  const [r, g, b] = rgb.map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
```

---

## 8. Security Architecture

### 8.1 End-to-End Encryption

#### Client-Side Encryption
```typescript
import { encrypt, decrypt } from 'openpgp';

class E2EEncryption {
  private keyPair: KeyPair | null = null;

  async generateKeyPair(userId: string, passphrase: string) {
    const { privateKey, publicKey } = await openpgp.generateKey({
      type: 'ecc',
      curve: 'curve25519',
      userIDs: [{ name: userId, email: `${userId}@app.local` }],
      passphrase
    });

    this.keyPair = { privateKey, publicKey };
    return { publicKey };
  }

  async encryptData(data: string, recipientPublicKey: string): Promise<string> {
    const encrypted = await openpgp.encrypt({
      message: await openpgp.createMessage({ text: data }),
      encryptionKeys: await openpgp.readKey({ armoredKey: recipientPublicKey }),
      signingKeys: this.keyPair?.privateKey
    });

    return encrypted;
  }

  async decryptData(encryptedData: string): Promise<string> {
    const message = await openpgp.readMessage({ armoredMessage: encryptedData });
    
    const { data: decrypted } = await openpgp.decrypt({
      message,
      decryptionKeys: this.keyPair?.privateKey,
      verificationKeys: this.keyPair?.publicKey
    });

    return decrypted;
  }
}
```

#### Field-Level Encryption
```typescript
class FieldEncryption {
  private masterKey: CryptoKey;

  async encryptField(plaintext: string): Promise<EncryptedField> {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encoder = new TextEncoder();
    
    const ciphertext = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      this.masterKey,
      encoder.encode(plaintext)
    );

    return {
      ciphertext: arrayBufferToBase64(ciphertext),
      iv: arrayBufferToBase64(iv),
      algorithm: 'AES-256-GCM'
    };
  }

  async decryptField(field: EncryptedField): Promise<string> {
    const iv = base64ToArrayBuffer(field.iv);
    const ciphertext = base64ToArrayBuffer(field.ciphertext);
    
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      this.masterKey,
      ciphertext
    );

    return new TextDecoder().decode(decrypted);
  }
}
```

### 8.2 Zero-Knowledge Architecture

```typescript
// Zero-knowledge: server never sees plaintext
class ZeroKnowledgeArchitecture {
  // Client derives encryption key from password
  async deriveKey(password: string, salt: Uint8Array): Promise<CryptoKey> {
    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(password),
      'PBKDF2',
      false,
      ['deriveBits', 'deriveKey']
    );

    return crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt,
        iterations: 600000,
        hash: 'SHA-256'
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt', 'decrypt']
    );
  }

  // Server stores only encrypted blob
  async syncToServer(encryptedData: EncryptedBlob) {
    await fetch('/api/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: encryptedData.ciphertext,
        iv: encryptedData.iv,
        version: encryptedData.version
      })
    });
  }
}
```

### 8.3 Secure Backup Strategies

#### Shamir's Secret Sharing
```typescript
import { split, combine } from 'shamir-secret-sharing';

class SecureBackup {
  // Split encryption key into shares
  async createBackupShares(masterKey: Uint8Array): Promise<BackupShares> {
    // Create 5 shares, require 3 to reconstruct
    const shares = await split(masterKey, 5, 3);
    
    return {
      share1: base64Encode(shares[0]), // Store locally
      share2: base64Encode(shares[1]), // Cloud storage 1
      share3: base64Encode(shares[2]), // Cloud storage 2
      share4: base64Encode(shares[3]), // Trusted contact
      share5: base64Encode(shares[4])  // Paper backup
    };
  }

  async recoverFromShares(shareData: string[]): Promise<Uint8Array> {
    const shares = shareData.map(s => base64Decode(s));
    return combine(shares);
  }
}
```

### 8.4 Authentication Patterns

#### Passkeys (WebAuthn)
```typescript
class PasskeyAuth {
  async registerPasskey(userId: string, username: string) {
    const challenge = await this.getRegistrationChallenge(userId);

    const credential = await navigator.credentials.create({
      publicKey: {
        challenge: base64ToBuffer(challenge),
        rp: { name: 'Productivity Dashboard', id: location.hostname },
        user: {
          id: new TextEncoder().encode(userId),
          name: username,
          displayName: username
        },
        pubKeyCredParams: [
          { alg: -7, type: 'public-key' },   // ES256
          { alg: -257, type: 'public-key' }  // RS256
        ],
        authenticatorSelection: {
          authenticatorAttachment: 'platform',
          userVerification: 'preferred'
        },
        timeout: 60000
      }
    });

    await this.verifyRegistration(credential);
  }

  async authenticateWithPasskey(): Promise<string> {
    const challenge = await this.getAuthenticationChallenge();

    const assertion = await navigator.credentials.get({
      publicKey: {
        challenge: base64ToBuffer(challenge),
        rpId: location.hostname,
        userVerification: 'preferred',
        timeout: 60000
      }
    });

    return this.verifyAuthentication(assertion);
  }
}
```

#### OAuth 2.0 + PKCE
```typescript
class OAuthManager {
  async initiateOAuth(provider: string) {
    // Generate PKCE parameters
    const codeVerifier = this.generateCodeVerifier();
    const codeChallenge = await this.generateCodeChallenge(codeVerifier);
    
    // Store code verifier for later
    sessionStorage.setItem('code_verifier', codeVerifier);

    // Build authorization URL
    const params = new URLSearchParams({
      client_id: CLIENT_ID,
      response_type: 'code',
      scope: 'openid profile email',
      redirect_uri: `${location.origin}/callback`,
      code_challenge: codeChallenge,
      code_challenge_method: 'S256',
      state: this.generateState()
    });

    location.href = `https://auth.provider.com/authorize?${params}`;
  }

  async handleCallback(code: string): Promise<Tokens> {
    const codeVerifier = sessionStorage.getItem('code_verifier');
    
    const response = await fetch('https://auth.provider.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: CLIENT_ID,
        code,
        redirect_uri: `${location.origin}/callback`,
        code_verifier: codeVerifier!
      })
    });

    return response.json();
  }
}
```

---

## 9. Performance Optimization

### 9.1 Virtual Scrolling for Large Lists

```typescript
// Already covered in Section 5.5 - see TanStack Virtual example
// Additional: react-window for simpler use cases

import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

function VirtualizedTaskList({ tasks }: { tasks: Task[] }) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <TaskItem task={tasks[index]} />
    </div>
  );

  return (
    <AutoSizer>
      {({ height, width }) => (
        <List
          height={height}
          itemCount={tasks.length}
          itemSize={72}
          width={width}
          overscanCount={5}
        >
          {Row}
        </List>
      )}
    </AutoSizer>
  );
}
```

### 9.2 Image Optimization Strategies

```typescript
// Responsive images with lazy loading
function OptimizedImage({ src, alt, sizes }: ImageProps) {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      srcSet={`
        ${src}?w=320 320w,
        ${src}?w=640 640w,
        ${src}?w=960 960w,
        ${src}?w=1280 1280w
      `}
      sizes={sizes}
      style={{ contentVisibility: 'auto' }}
    />
  );
}

// Image CDN integration (Cloudinary example)
function getOptimizedImageUrl(publicId: string, options: ImageOptions): string {
  const transformations = [
    `w_${options.width}`,
    `h_${options.height}`,
    'c_fill',
    'q_auto',
    'f_auto',
    'dpr_auto'
  ];

  return `https://res.cloudinary.com/demo/image/upload/${transformations.join(',')}/${publicId}`;
}
```

### 9.3 Code Splitting and Lazy Loading

```typescript
// Route-based code splitting
const Dashboard = lazy(() => import(/* webpackChunkName: "dashboard" */ './pages/Dashboard'));
const Analytics = lazy(() => import(/* webpackChunkName: "analytics" */ './pages/Analytics'));

// Component-level code splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));

// Preload on hover
function PreloadLink({ to, children }: { to: string; children: React.ReactNode }) {
  const prefetch = () => {
    const component = import(`./pages/${to}`);
  };

  return (
    <Link to={to} onMouseEnter={prefetch}>
      {children}
    </Link>
  );
}

// Dynamic imports for heavy libraries
async function loadChartLibrary() {
  const { Chart } = await import('chart.js/auto');
  return Chart;
}
```

### 9.4 Memory Management

```typescript
// Cleanup subscriptions
function useTaskSubscription(taskId: string) {
  const [task, setTask] = useState<Task | null>(null);

  useEffect(() => {
    const unsubscribe = db.tasks.subscribe(taskId, setTask);
    
    return () => {
      unsubscribe();
    };
  }, [taskId]);

  return task;
}

// WeakMap for caching without preventing GC
const cache = new WeakMap<object, any>();

function getCachedValue(key: object, compute: () => any) {
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const value = compute();
  cache.set(key, value);
  return value;
}

// Debounce expensive operations
function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    (...args: Parameters<T>) => {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => callback(...args), delay);
    },
    [callback, delay]
  ) as T;
}

// Virtual list for memory efficiency
// See Section 9.1 for implementation
```

---

## 10. Analytics & Insights

### 10.1 Productivity Metrics Calculation

```typescript
interface ProductivityMetrics {
  tasksCompleted: number;
  tasksCreated: number;
  completionRate: number;
  averageCompletionTime: number; // hours
  focusTime: number; // minutes
  contextSwitches: number;
  productivityScore: number; // 0-100
}

class ProductivityAnalyzer {
  calculateMetrics(tasks: Task[], timeRange: DateRange): ProductivityMetrics {
    const filteredTasks = tasks.filter(t => 
      t.createdAt >= timeRange.start && t.createdAt <= timeRange.end
    );

    const completed = filteredTasks.filter(t => t.completed);
    const completionTimes = completed
      .filter(t => t.completedAt)
      .map(t => (t.completedAt!.getTime() - t.createdAt.getTime()) / 3600000);

    return {
      tasksCompleted: completed.length,
      tasksCreated: filteredTasks.length,
      completionRate: completed.length / filteredTasks.length,
      averageCompletionTime: this.average(completionTimes),
      focusTime: this.calculateFocusTime(filteredTasks),
      contextSwitches: this.countContextSwitches(filteredTasks),
      productivityScore: this.calculateProductivityScore(completed, filteredTasks)
    };
  }

  private calculateProductivityScore(completed: Task[], all: Task[]): number {
    const completionRate = completed.length / all.length;
    const onTimeRate = completed.filter(t => 
      !t.dueDate || t.completedAt! <= t.dueDate
    ).length / (completed.length || 1);

    return Math.round((completionRate * 0.6 + onTimeRate * 0.4) * 100);
  }
}
```

### 10.2 Time Tracking Analysis

```typescript
interface TimeEntry {
  taskId: string;
  startTime: Date;
  endTime?: Date;
  duration?: number; // seconds
}

class TimeTracker {
  private activeTimers: Map<string, TimeEntry> = new Map();

  startTracking(taskId: string) {
    const entry: TimeEntry = {
      taskId,
      startTime: new Date()
    };
    
    this.activeTimers.set(taskId, entry);
  }

  stopTracking(taskId: string): TimeEntry {
    const entry = this.activeTimers.get(taskId);
    if (!entry) throw new Error('Timer not found');

    entry.endTime = new Date();
    entry.duration = (entry.endTime.getTime() - entry.startTime.getTime()) / 1000;
    
    this.activeTimers.delete(taskId);
    this.saveEntry(entry);
    
    return entry;
  }

  async getTimeReport(timeRange: DateRange): Promise<TimeReport> {
    const entries = await this.getEntries(timeRange);
    
    const byTask = groupBy(entries, 'taskId');
    const byDay = groupBy(entries, e => e.startTime.toISOString().split('T')[0]);

    return {
      totalTime: sum(entries.map(e => e.duration || 0)),
      byTask: mapValues(byTask, entries => sum(entries.map(e => e.duration || 0))),
      byDay: mapValues(byDay, entries => sum(entries.map(e => e.duration || 0))),
      averageSessionLength: average(entries.map(e => e.duration || 0))
    };
  }
}
```

### 10.3 Habit Streak Algorithms

```typescript
interface Habit {
  id: string;
  name: string;
  frequency: 'daily' | 'weekly' | 'custom';
  targetDays: number[]; // 0-6 for weekly
  completions: Date[];
}

class HabitStreakCalculator {
  calculateStreak(habit: Habit): number {
    const sorted = [...habit.completions].sort((a, b) => b.getTime() - a.getTime());
    
    if (sorted.length === 0) return 0;
    
    let streak = 0;
    let currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0);

    for (const completion of sorted) {
      const completionDate = new Date(completion);
      completionDate.setHours(0, 0, 0, 0);
      
      const diffDays = Math.floor(
        (currentDate.getTime() - completionDate.getTime()) / 86400000
      );

      if (diffDays === 0 || diffDays === 1) {
        streak++;
        currentDate = completionDate;
      } else {
        break;
      }
    }

    return streak;
  }

  calculateLongestStreak(habit: Habit): number {
    const sorted = [...habit.completions].sort((a, b) => a.getTime() - b.getTime());
    
    let maxStreak = 0;
    let currentStreak = 0;
    let previousDate: Date | null = null;

    for (const completion of sorted) {
      const completionDate = new Date(completion);
      completionDate.setHours(0, 0, 0, 0);

      if (previousDate) {
        const diffDays = Math.floor(
          (completionDate.getTime() - previousDate.getTime()) / 86400000
        );

        if (diffDays === 1) {
          currentStreak++;
        } else {
          maxStreak = Math.max(maxStreak, currentStreak);
          currentStreak = 1;
        }
      } else {
        currentStreak = 1;
      }

      previousDate = completionDate;
    }

    return Math.max(maxStreak, currentStreak);
  }
}
```

### 10.4 Predictive Analytics

```typescript
class PredictiveAnalytics {
  private mlModel: MLModel;

  // Predict task completion time
  async predictCompletionTime(task: Task): Promise<number> {
    const features = this.extractFeatures(task);
    const prediction = await this.mlModel.predict(features);
    
    return prediction.estimatedHours;
  }

  // Predict optimal task scheduling
  async suggestBestTime(task: Task): Promise<Date[]> {
    const userPatterns = await this.getUserProductivityPatterns();
    const taskType = this.classifyTaskType(task);
    
    // Find times when user is most productive for this task type
    const optimalSlots = userPatterns
      .filter(p => p.taskType === taskType && p.productivity > 0.8)
      .map(p => p.timeOfDay);

    return this.getUpcomingSlots(optimalSlots, 5);
  }

  // Predict burnout risk
  async assessBurnoutRisk(userId: string): Promise<BurnoutRisk> {
    const recentMetrics = await this.getRecentMetrics(userId, 14);
    
    const riskFactors = {
      overwork: recentMetrics.dailyHours > 10,
      poorSleep: recentMetrics.sleepQuality < 0.6,
      missedDeadlines: recentMetrics.missedDeadlines > 2,
      decliningProductivity: this.isDeclining(recentMetrics.productivityTrend)
    };

    const riskScore = Object.values(riskFactors).filter(Boolean).length / 4;

    return {
      score: riskScore,
      level: riskScore > 0.75 ? 'high' : riskScore > 0.5 ? 'medium' : 'low',
      factors: riskFactors
    };
  }

  private extractFeatures(task: Task): FeatureVector {
    return {
      titleLength: task.title.length,
      descriptionLength: task.description?.length || 0,
      hasDueDate: task.dueDate ? 1 : 0,
      daysUntilDue: task.dueDate ? 
        Math.floor((task.dueDate.getTime() - Date.now()) / 86400000) : 365,
      tagCount: task.tags.length,
      priority: ['low', 'medium', 'high', 'urgent'].indexOf(task.priority),
      similarTasksAvgTime: this.getSimilarTasksAvgTime(task)
    };
  }
}
```

---

## Implementation Recommendations Summary

### Recommended Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React + TypeScript | Type safety, ecosystem, performance |
| **State Management** | Zustand + TanStack Query | Simple, effective, great for server state |
| **Database** | SQLite (local) + Postgres (server) | Offline-first, sync capability |
| **Sync** | Electric SQL or Yjs | Proven sync engines |
| **Mobile** | Capacitor | Maximum code sharing |
| **AI** | LangChain + OpenAI API | Flexible, powerful |
| **Real-time** | Socket.io or Yjs | Reliable, well-supported |
| **Auth** | Passkeys + OAuth 2.0 | Modern, secure |

### Architecture Principles

1. **Offline-First:** Design for no connectivity, enhance with sync
2. **Progressive Enhancement:** Core features work without AI, enhanced with AI
3. **Security by Default:** E2E encryption for sensitive data
4. **Accessibility First:** WCAG 2.1 AA compliance minimum
5. **Performance Budget:** First contentful paint < 1.5s, TTI < 3.5s

### Development Phases

1. **Phase 1:** Core task management, offline storage, basic sync
2. **Phase 2:** AI integration (RAG, prioritization), voice commands
3. **Phase 3:** Real-time collaboration, plugins, advanced analytics
4. **Phase 4:** Mobile apps, advanced security, enterprise features

---

*Research compiled from official documentation, GitHub repositories, and best practice guides as of March 30, 2026.*
