importScripts('https://unpkg.com/dexie/dist/dexie.js');

const db = new Dexie("GranSabanaDB");
db.version(1).stores({ envios: '++id, status' });

self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-visitas') {
        event.waitUntil(enviarPendientes());
    }
});

async function enviarPendientes() {
    const pendientes = await db.envios.where('status').equals('pendiente').toArray();
    for (const item of pendientes) {
        try {
            const res = await fetch('/api/enviar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(item)
            });
            if (res.ok) {
                // Si se envió, lo borramos de IndexedDB
                await db.envios.delete(item.id);
            }
        } catch (error) {
            console.error("Error sincronizando en background", error);
            throw error; // Fuerza el reintento más tarde
        }
    }
}