import { Pool } from 'pg';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import {
  monthlyData,
  channelData,
  userData,
  inputTypeData,
  outputTypeData,
  languageData,
  platformPublishData
} from '../src/data/kpiData.js'; // Note: using .js extension for TS runtime compatibility if needed, but tsx handles .ts without extension

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from d:\ChatBot\.env
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

if (!process.env.DATABASE_URL) {
  console.error('DATABASE_URL is missing in the root .env file!');
  process.exit(1);
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

async function runSeed() {
  const client = await pool.connect();
  try {
    console.log('🌱 Starting database seed...');
    
    // 1. Create Tables
    await client.query(`
      DROP TABLE IF EXISTS monthly_data CASCADE;
      CREATE TABLE monthly_data (
        id SERIAL PRIMARY KEY,
        month VARCHAR(50) NOT NULL,
        uploaded INT,
        created INT,
        published INT,
        growthRate NUMERIC,
        uploadedDuration NUMERIC,
        createdDuration NUMERIC
      );
      
      DROP TABLE IF EXISTS channel_data CASCADE;
      CREATE TABLE channel_data (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        uploaded INT,
        created INT,
        published INT,
        publishRate NUMERIC,
        uploadedDuration VARCHAR(50),
        createdDuration VARCHAR(50),
        publishedDuration VARCHAR(50)
      );
      
      DROP TABLE IF EXISTS user_data CASCADE;
      CREATE TABLE user_data (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        uploaded INT,
        created INT,
        published INT,
        publishRate NUMERIC,
        uploadedDuration VARCHAR(50),
        createdDuration VARCHAR(50),
        publishedDuration VARCHAR(50)
      );
      
      DROP TABLE IF EXISTS input_type_data CASCADE;
      CREATE TABLE input_type_data (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        uploaded INT,
        created INT,
        published INT,
        publishAffinity NUMERIC
      );

      DROP TABLE IF EXISTS output_type_data CASCADE;
      CREATE TABLE output_type_data (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        uploaded INT,
        created INT,
        published INT,
        publishRate NUMERIC
      );

      DROP TABLE IF EXISTS language_data CASCADE;
      CREATE TABLE language_data (
        id SERIAL PRIMARY KEY,
        language VARCHAR(100) NOT NULL,
        uploaded INT,
        created INT,
        published INT,
        publishRate NUMERIC
      );

      DROP TABLE IF EXISTS platform_publish_data CASCADE;
      CREATE TABLE platform_publish_data (
        id SERIAL PRIMARY KEY,
        channel VARCHAR(50) NOT NULL,
        facebook INT,
        instagram INT,
        linkedin INT,
        reels INT,
        shorts INT,
        x INT,
        youtube INT,
        threads INT,
        total INT
      );
    `);
    
    console.log('✅ Tables created successfully.');

    // 2. Insert Data
    for (const d of monthlyData) {
      await client.query(
        'INSERT INTO monthly_data (month, uploaded, created, published, growthRate, uploadedDuration, createdDuration) VALUES ($1, $2, $3, $4, $5, $6, $7)',
        [d.month, d.uploaded, d.created, d.published, d.growthRate || 0, d.uploadedDuration || 0, d.createdDuration || 0]
      );
    }
    
    for (const d of channelData) {
      await client.query(
        'INSERT INTO channel_data (name, uploaded, created, published, publishRate, uploadedDuration, createdDuration, publishedDuration) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
        [d.name, d.uploaded, d.created, d.published, d.publishRate, d.uploadedDuration, d.createdDuration, d.publishedDuration]
      );
    }
    
    for (const d of userData) {
      await client.query(
        'INSERT INTO user_data (name, uploaded, created, published, publishRate, uploadedDuration, createdDuration, publishedDuration) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
        [d.name, d.uploaded, d.created, d.published, d.publishRate, d.uploadedDuration, d.createdDuration, d.publishedDuration]
      );
    }
    
    for (const d of inputTypeData) {
      await client.query(
        'INSERT INTO input_type_data (name, uploaded, created, published, publishAffinity) VALUES ($1, $2, $3, $4, $5)',
        [d.name, d.uploaded, d.created, d.published, d.publishAffinity]
      );
    }
    
    for (const d of outputTypeData) {
      await client.query(
        'INSERT INTO output_type_data (name, uploaded, created, published, publishRate) VALUES ($1, $2, $3, $4, $5)',
        [d.name, d.uploaded, d.created, d.published, d.publishRate]
      );
    }
    
    for (const d of languageData) {
      await client.query(
        'INSERT INTO language_data (language, uploaded, created, published, publishRate) VALUES ($1, $2, $3, $4, $5)',
        [d.language, d.uploaded, d.created, d.published, d.publishRate]
      );
    }
    
    for (const d of platformPublishData) {
      await client.query(
        'INSERT INTO platform_publish_data (channel, facebook, instagram, linkedin, reels, shorts, x, youtube, threads, total) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
        [d.channel, d.facebook, d.instagram, d.linkedin, d.reels, d.shorts, d.x, d.youtube, d.threads, d.total]
      );
    }

    console.log('✅ All data inserted successfully!');

  } catch (error) {
    console.error('❌ Seeding failed:', error);
  } finally {
    client.release();
    pool.end();
  }
}

runSeed();
