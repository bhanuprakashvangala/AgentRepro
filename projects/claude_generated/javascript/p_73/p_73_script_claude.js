const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
require('dotenv').config();

class StripeService {
  constructor() {
    this.stripe = stripe;
    this.webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  }

  /**
   * Create checkout session
   */
  async createCheckoutSession({ priceId, successUrl, cancelUrl, customerId }) {
    try {
      const session = await this.stripe.checkout.sessions.create({
        mode: 'payment',
        customer: customerId,
        line_items: [
          {
            price: priceId,
            quantity: 1
          }
        ],
        success_url: successUrl,
        cancel_url: cancelUrl
      });

      return session;
    } catch (error) {
      throw new Error(`Checkout session creation failed: ${error.message}`);
    }
  }

  /**
   * Create customer
   */
  async createCustomer({ email, name, metadata }) {
    try {
      const customer = await this.stripe.customers.create({
        email,
        name,
        metadata
      });

      return customer;
    } catch (error) {
      throw new Error(`Customer creation failed: ${error.message}`);
    }
  }

  /**
   * Create subscription
   */
  async createSubscription({ customerId, priceId }) {
    try {
      const subscription = await this.stripe.subscriptions.create({
        customer: customerId,
        items: [{ price: priceId }],
        payment_behavior: 'default_incomplete',
        payment_settings: { save_default_payment_method: 'on_subscription' },
        expand: ['latest_invoice.payment_intent']
      });

      return subscription;
    } catch (error) {
      throw new Error(`Subscription creation failed: ${error.message}`);
    }
  }

  /**
   * Cancel subscription
   */
  async cancelSubscription(subscriptionId) {
    try {
      const subscription = await this.stripe.subscriptions.cancel(subscriptionId);
      return subscription;
    } catch (error) {
      throw new Error(`Subscription cancellation failed: ${error.message}`);
    }
  }

  /**
   * Create payment intent
   */
  async createPaymentIntent({ amount, currency = 'usd', customerId }) {
    try {
      const paymentIntent = await this.stripe.paymentIntents.create({
        amount: amount * 100, // Convert to cents
        currency,
        customer: customerId,
        automatic_payment_methods: { enabled: true }
      });

      return paymentIntent;
    } catch (error) {
      throw new Error(`Payment intent creation failed: ${error.message}`);
    }
  }

  /**
   * Refund payment
   */
  async refundPayment(paymentIntentId, amount) {
    try {
      const refund = await this.stripe.refunds.create({
        payment_intent: paymentIntentId,
        amount: amount ? amount * 100 : undefined
      });

      return refund;
    } catch (error) {
      throw new Error(`Refund failed: ${error.message}`);
    }
  }

  /**
   * List customer payments
   */
  async listPayments(customerId, limit = 10) {
    try {
      const charges = await this.stripe.charges.list({
        customer: customerId,
        limit
      });

      return charges.data;
    } catch (error) {
      throw new Error(`Failed to list payments: ${error.message}`);
    }
  }

  /**
   * Handle webhook event
   */
  handleWebhook(rawBody, signature) {
    try {
      const event = this.stripe.webhooks.constructEvent(
        rawBody,
        signature,
        this.webhookSecret
      );

      return event;
    } catch (error) {
      throw new Error(`Webhook verification failed: ${error.message}`);
    }
  }
}

module.exports = StripeService;

// Example server
if (require.main === module) {
  const express = require('express');
  const app = express();

  const stripeService = new StripeService();

  app.post('/create-checkout', express.json(), async (req, res) => {
    try {
      const { priceId } = req.body;
      const session = await stripeService.createCheckoutSession({
        priceId,
        successUrl: 'http://localhost:3000/success',
        cancelUrl: 'http://localhost:3000/cancel'
      });

      res.json({ url: session.url });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const signature = req.headers['stripe-signature'];

    try {
      const event = stripeService.handleWebhook(req.body, signature);

      console.log('Webhook event:', event.type);

      switch (event.type) {
        case 'payment_intent.succeeded':
          console.log('Payment succeeded:', event.data.object);
          break;
        case 'customer.subscription.created':
          console.log('Subscription created:', event.data.object);
          break;
        case 'customer.subscription.deleted':
          console.log('Subscription deleted:', event.data.object);
          break;
        default:
          console.log('Unhandled event type:', event.type);
      }

      res.json({ received: true });
    } catch (error) {
      console.error('Webhook error:', error);
      res.status(400).send(`Webhook Error: ${error.message}`);
    }
  });

  const PORT = 3000;
  app.listen(PORT, () => {
    console.log(`Stripe server running on port ${PORT}`);
  });
}
