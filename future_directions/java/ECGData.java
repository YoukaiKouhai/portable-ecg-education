package ecg;

public class ECGData {

    public double[] t;
    public double[] leadI;
    public double[] leadII;

    public double recordTime;

    public ECGData(double[] t, double[] I, double[] II) {

        this.t = t;
        this.leadI = I;
        this.leadII = II;

        this.recordTime = t[t.length - 1];
    }

    public int size() {
        return t.length;
    }
}