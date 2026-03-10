package ecg.filter;

public class FilterPipeline {

    public static double[] applyPipeline(double[] signal, double Fs) {

        double[] butter = ButterworthBandpass.filter(signal, Fs);

        double[] notch = ChebyshevNotch.filter(butter, Fs);

        double[] ref = LMSFilter.generate60HzReference(signal.length, Fs);

        double[] adaptive = LMSFilter.filter(notch, ref, 0.01);

        return adaptive;
    }

}