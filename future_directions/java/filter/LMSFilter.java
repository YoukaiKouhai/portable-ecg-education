package ecg.filter;

public class LMSFilter {

    public static double[] filter(double[] signal, double[] reference, double mu) {

        double w = 0;

        double[] y = new double[signal.length];

        for (int n = 0; n < signal.length; n++) {

            y[n] = signal[n] - w * reference[n];

            w = w + mu * y[n] * reference[n];
        }

        return y;
    }

    public static double[] generate60HzReference(int length, double Fs) {

        double[] ref = new double[length];

        for (int i = 0; i < length; i++)
            ref[i] = Math.sin(2 * Math.PI * 60 * i / Fs);

        return ref;
    }

}