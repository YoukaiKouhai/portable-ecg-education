package ecg.filter;

public class ChebyshevNotch {

    public static double[] filter(double[] x, double Fs) {

        double f0 = 60.0;
        double Q = 30.0;

        double w0 = 2 * Math.PI * f0 / Fs;

        double alpha = Math.sin(w0) / (2 * Q);

        double b0 = 1;
        double b1 = -2 * Math.cos(w0);
        double b2 = 1;

        double a0 = 1 + alpha;
        double a1 = -2 * Math.cos(w0);
        double a2 = 1 - alpha;

        double[] y = new double[x.length];

        for (int i = 2; i < x.length; i++) {

            y[i] =
                (b0/a0)*x[i] +
                (b1/a0)*x[i-1] +
                (b2/a0)*x[i-2] -
                (a1/a0)*y[i-1] -
                (a2/a0)*y[i-2];
        }

        return y;
    }
}