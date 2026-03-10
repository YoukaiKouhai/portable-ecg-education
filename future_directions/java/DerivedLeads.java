package ecg;

public class DerivedLeads {

    public double[] leadIII;
    public double[] aVR;
    public double[] aVL;
    public double[] aVF;

    public DerivedLeads(double[] III, double[] VR, double[] VL, double[] VF) {

        this.leadIII = III;
        this.aVR = VR;
        this.aVL = VL;
        this.aVF = VF;
    }
}