const { MongoClient } = require('mongodb');

class AggregationHelper {
  constructor(connectionString, dbName) {
    this.connectionString = connectionString || 'mongodb://localhost:27017';
    this.dbName = dbName;
    this.client = null;
    this.db = null;
  }

  async connect() {
    try {
      this.client = new MongoClient(this.connectionString);
      await this.client.connect();
      this.db = this.client.db(this.dbName);
      console.log(`Connected to MongoDB database: ${this.dbName}`);
      return true;
    } catch (error) {
      console.error('MongoDB connection error:', error);
      throw error;
    }
  }

  async disconnect() {
    if (this.client) {
      await this.client.close();
      console.log('Disconnected from MongoDB');
    }
  }

  /**
   * Get total count grouped by field
   */
  async getTotalsByField(collectionName, groupField) {
    const collection = this.db.collection(collectionName);
    return await collection.aggregate([
      { $group: { _id: `$${groupField}`, count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]).toArray();
  }

  /**
   * Get average value by field
   */
  async getAverageByField(collectionName, groupField, valueField) {
    const collection = this.db.collection(collectionName);
    return await collection.aggregate([
      { $group: { _id: `$${groupField}`, average: { $avg: `$${valueField}` } } },
      { $sort: { average: -1 } }
    ]).toArray();
  }

  /**
   * Get top N documents
   */
  async getTopN(collectionName, sortField, limit = 10, ascending = false) {
    const collection = this.db.collection(collectionName);
    return await collection.aggregate([
      { $sort: { [sortField]: ascending ? 1 : -1 } },
      { $limit: limit }
    ]).toArray();
  }

  /**
   * Get documents within date range
   */
  async getDateRangeStats(collectionName, dateField, startDate, endDate) {
    const collection = this.db.collection(collectionName);
    return await collection.aggregate([
      {
        $match: {
          [dateField]: {
            $gte: new Date(startDate),
            $lte: new Date(endDate)
          }
        }
      },
      {
        $group: {
          _id: null,
          count: { $sum: 1 },
          minDate: { $min: `$${dateField}` },
          maxDate: { $max: `$${dateField}` }
        }
      }
    ]).toArray();
  }

  /**
   * Custom aggregation pipeline
   */
  async runPipeline(collectionName, pipeline) {
    const collection = this.db.collection(collectionName);
    return await collection.aggregate(pipeline).toArray();
  }

  /**
   * Pipeline builder
   */
  pipelineBuilder() {
    const pipeline = [];

    return {
      match(criteria) {
        pipeline.push({ $match: criteria });
        return this;
      },
      group(groupSpec) {
        pipeline.push({ $group: groupSpec });
        return this;
      },
      sort(sortSpec) {
        pipeline.push({ $sort: sortSpec });
        return this;
      },
      limit(count) {
        pipeline.push({ $limit: count });
        return this;
      },
      project(fields) {
        pipeline.push({ $project: fields });
        return this;
      },
      lookup(from, localField, foreignField, as) {
        pipeline.push({ $lookup: { from, localField, foreignField, as } });
        return this;
      },
      unwind(path) {
        pipeline.push({ $unwind: path });
        return this;
      },
      build() {
        return pipeline;
      }
    };
  }
}

module.exports = AggregationHelper;

// Example usage
if (require.main === module) {
  const helper = new AggregationHelper('mongodb://localhost:27017', 'testdb');

  helper.connect().then(async () => {
    console.log('Aggregation helper ready!');

    // Example: Build custom pipeline
    const pipeline = helper.pipelineBuilder()
      .match({ status: 'active' })
      .group({ _id: '$category', total: { $sum: '$amount' } })
      .sort({ total: -1 })
      .limit(5)
      .build();

    console.log('Pipeline:', JSON.stringify(pipeline, null, 2));

    await helper.disconnect();
  }).catch(console.error);
}
