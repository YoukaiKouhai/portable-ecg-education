package ecg;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

public class PortableECGAnalyzer {

    static double VREF = 5.0;
    static int ADCMAX = 1023;

    public static void main(String[] args) throws Exception {

        String folder = createRunFolder();
        System.out.println("Saving data to: " + folder);

        ECGData data = loadCSV();

        double Fs = data.size() / data.recordTime;

        System.out.println("Estimated Sampling Rate: " + Fs);

        double[] leadI = convertToMilliVolts(data.leadI);
        double[] leadII = convertToMilliVolts(data.leadII);

        DerivedLeads derived = computeDerivedLeads(leadI, leadII);

        double hr = estimateHeartRate(leadII, Fs);

        System.out.println("Estimated Heart Rate: " + hr + " BPM");

        saveFiltered(folder, data.t, leadI, leadII);

        FilterPipeline.applyAllFilters(folder, data.t, data.leadI, data.leadII, Fs);
    }

    static String createRunFolder() throws IOException {

        Path base = Paths.get("").toAbsolutePath();

        int max = 0;

        try (DirectoryStream<Path> stream = Files.newDirectoryStream(base)) {

            for (Path p : stream) {

                String name = p.getFileName().toString();

                if (name.startsWith("RUN_")) {

                    int num = Integer.parseInt(name.substring(4));

                    max = Math.max(max, num);
                }
            }
        }

        int next = max + 1;

        String folder = String.format("RUN_%03d", next);

        Path run = base.resolve(folder);

        Files.createDirectories(run);

        return run.toString();
    }

    static ECGData loadCSV() throws Exception {

        Scanner scanner = new Scanner(System.in);

        System.out.println("Enter CSV path:");

        String path = scanner.nextLine();

        List<Double> t = new ArrayList<>();
        List<Double> leadI = new ArrayList<>();
        List<Double> leadII = new ArrayList<>();

        BufferedReader br = new BufferedReader(new FileReader(path));

        String header = br.readLine();

        String line;

        while ((line = br.readLine()) != null) {

            String[] parts = line.split(",");

            t.add(Double.parseDouble(parts[0]));
            leadI.add(Double.parseDouble(parts[1]));
            leadII.add(Double.parseDouble(parts[2]));
        }

        br.close();

        return new ECGData(
                toArray(t),
                toArray(leadI),
                toArray(leadII)
        );
    }

    static double[] convertToMilliVolts(double[] raw) {

        double mean = Arrays.stream(raw).average().orElse(0);

        double[] out = new double[raw.length];

        for (int i = 0; i < raw.length; i++) {

            double v = (raw[i] / ADCMAX) * VREF;

            v -= mean;

            out[i] = v * 1000;
        }

        return out;
    }

    static DerivedLeads computeDerivedLeads(double[] I, double[] II) {

        int n = I.length;

        double[] III = new double[n];
        double[] aVR = new double[n];
        double[] aVL = new double[n];
        double[] aVF = new double[n];

        for (int i = 0; i < n; i++) {

            III[i] = II[i] - I[i];
            aVR[i] = -(I[i] + II[i]) / 2;
            aVL[i] = I[i] - II[i] / 2;
            aVF[i] = II[i] - I[i] / 2;
        }

        return new DerivedLeads(III, aVR, aVL, aVF);
    }

    static double estimateHeartRate(double[] ecg, double Fs) {

        double mean = Arrays.stream(ecg).average().orElse(0);

        double max = Arrays.stream(ecg).max().orElse(1);

        List<Integer> peaks = new ArrayList<>();

        int minDist = (int)(0.4 * Fs);

        for (int i = 1; i < ecg.length - 1; i++) {

            if (ecg[i] > ecg[i-1] &&
                ecg[i] > ecg[i+1] &&
                ecg[i] > 0.5 * max) {

                if (peaks.isEmpty() || i - peaks.get(peaks.size()-1) > minDist)
                    peaks.add(i);
            }
        }

        if (peaks.size() < 2) return 0;

        List<Double> rr = new ArrayList<>();

        for (int i = 1; i < peaks.size(); i++)
            rr.add((peaks.get(i) - peaks.get(i-1)) / Fs);

        double meanRR = rr.stream().mapToDouble(Double::doubleValue).average().orElse(1);

        return 60.0 / meanRR;
    }

    static void saveFiltered(String folder, double[] t, double[] I, double[] II) throws Exception {

        FileWriter fw = new FileWriter(folder + "/filtered_ecg.csv");

        fw.write("t,leadI,leadII\n");

        for (int i = 0; i < t.length; i++) {

            fw.write(t[i] + "," + I[i] + "," + II[i] + "\n");
        }

        fw.close();
    }

    static double[] toArray(List<Double> list) {

        double[] arr = new double[list.size()];

        for (int i = 0; i < arr.length; i++)
            arr[i] = list.get(i);

        return arr;
    }

}