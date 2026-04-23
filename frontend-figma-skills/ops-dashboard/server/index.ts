import express from 'express';
import cors from 'cors';
import { Pool } from 'pg';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import multer from 'multer';
import { parse } from 'csv-parse';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from d:\ChatBot\.env
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

if (!process.env.DATABASE_URL) {
  console.error('DATABASE_URL is missing in the .env file!');
  process.exit(1);
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

app.get('/api/dashboard-data', async (req, res) => {
  try {
    const [
      monthlyRes,
      channelRes,
      userRes,
      inputTypeRes,
      outputTypeRes,
      languageRes,
      platformPublishRes
    ] = await Promise.all([
      pool.query('SELECT * FROM monthly_data ORDER BY id ASC'),
      pool.query('SELECT * FROM channel_data ORDER BY id ASC'),
      pool.query('SELECT * FROM user_data ORDER BY id ASC'),
      pool.query('SELECT * FROM input_type_data ORDER BY id ASC'),
      pool.query('SELECT * FROM output_type_data ORDER BY id ASC'),
      pool.query('SELECT * FROM language_data ORDER BY id ASC'),
      pool.query('SELECT * FROM platform_publish_data ORDER BY id ASC')
    ]);

    res.json({
      monthlyData: monthlyRes.rows,
      channelData: channelRes.rows,
      userData: userRes.rows,
      inputTypeData: inputTypeRes.rows,
      outputTypeData: outputTypeRes.rows,
      languageData: languageRes.rows,
      platformPublishData: platformPublishRes.rows
    });
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

const upload = multer({ dest: 'uploads/' });

app.post('/api/upload-csv', upload.single('file'), async (req, res) => {
  try {
    const { dataType } = req.body;
    if (!req.file) {
      return res.status(400).json({ error: 'No CSV file uploaded' });
    }

    const filePath = req.file.path;
    const results: any[] = [];

    fs.createReadStream(filePath)
      .pipe(parse({ columns: true, skip_empty_lines: true }))
      .on('data', (data) => results.push(data))
      .on('end', async () => {
        const client = await pool.connect();
        try {
          await client.query('BEGIN');

          if (dataType === 'userData') {
            for (const row of results) {
              const name = row['User'];
              const uploaded = parseInt(row['Uploaded Count']) || 0;
              const created = parseInt(row['Created Count']) || 0;
              const published = parseInt(row['Published Count']) || 0;
              const upDur = row['Uploaded Duration (hh:mm:ss)'] || '00:00:00';
              const crDur = row['Created Duration (hh:mm:ss)'] || '00:00:00';
              const pubDur = row['Published Duration (hh:mm:ss)'] || '00:00:00';

              if (name) {
                await client.query(`
                  INSERT INTO user_data (name, uploaded, created, published, "uploadedduration", "createdduration", "publishedduration")
                  VALUES ($1, $2, $3, $4, $5, $6, $7)
                  ON CONFLICT (name) DO UPDATE SET
                    uploaded = EXCLUDED.uploaded,
                    created = EXCLUDED.created,
                    published = EXCLUDED.published,
                    "uploadedduration" = EXCLUDED."uploadedduration",
                    "createdduration" = EXCLUDED."createdduration",
                    "publishedduration" = EXCLUDED."publishedduration"
                `, [name, uploaded, created, published, upDur, crDur, pubDur]);
              }
            }
          } else {
            throw new Error('Unsupported data type for insertion: ' + dataType);
          }

          await client.query('COMMIT');
          fs.unlinkSync(filePath); // Cleanup temp file
          res.json({ message: 'CSV Data successfully upserted.', rowsProcessed: results.length });
        } catch (dbError) {
          await client.query('ROLLBACK');
          fs.unlinkSync(filePath); // Cleanup temp file
          console.error('DB Insert Error:', dbError);
          res.status(500).json({ error: 'Failed to insert data into database.' });
        } finally {
          client.release();
        }
      })
      .on('error', (err) => {
        fs.unlinkSync(filePath);
        console.error('CSV Parsing Error:', err);
        res.status(500).json({ error: 'Failed to parse CSV file.' });
      });
  } catch (err: any) {
    console.error('Upload handling error:', err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 API Server running on http://localhost:${PORT}`);
});
