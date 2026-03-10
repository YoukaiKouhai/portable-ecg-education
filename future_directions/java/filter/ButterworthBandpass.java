package ecg.filter;

public class ButterworthBandpass {

    public static double[] filter(double[] signal, double fs) {

        double lowCut = 0.5;
        double highCut = 40.0;

        double dt = 1.0 / fs;

        double RC_low = 1.0 / (2 * Math.PI * highCut);
        double alpha_low = dt / (RC_low + dt);

        double RC_high = 1.0 / (2 * Math.PI * lowCut);
        double alpha_high = RC_high / (RC_high + dt);

        double[] hp = new double[signal.length];
        double[] bp = new double[signal.length];

        hp[0] = signal[0];

        for (int i = 1; i < signal.length; i++)
            hp[i] = alpha_high * (hp[i-1] + signal[i] - signal[i-1]);

        bp[0] = hp[0];

        for (int i = 1; i < hp.length; i++)
            bp[i] = bp[i-1] + alpha_low * (hp[i] - bp[i-1]);

        return bp;
    }

}