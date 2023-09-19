import io
import sys
import numpy as np
import scipy.io.wavfile
import pyrubberband as pyrb
from pydub import AudioSegment as aus

diphones = ["ހަން", "ހުން", "ގައި", "ޕޯސް"]
stretch = ["ނީ", "ބާ", "ވާ", "ފީ", "ދާ", "ތީ", "ޏާ", "ޒާ"]

def speedmod(seg, speed = 1.0, n = 0):
    seg_ch = seg.split_to_mono()
    samples = [s.get_array_of_samples() for s in seg_ch]
    alt_seg = np.array(samples).T.astype(np.float64)
    alt_seg /= np.iinfo(samples[0].typecode).max
    alt_seg = pyrb.time_stretch(alt_seg, sr=44100, rate=speed)
    alt_seg = pyrb.pitch_shift(alt_seg, sr=44100, n_steps=n)
    alt_seg = np.float32(alt_seg)

    wav_io = io.BytesIO()
    scipy.io.wavfile.write(wav_io, 44100, alt_seg)
    wav_io.seek(0)
    alt_seg = aus.from_wav(wav_io)

    return alt_seg.set_sample_width(2)

def generate_sentence(path, out, sentence):

    genenrated_sentence = aus.from_wav(path+"space.wav")
    siter = iter(range(0,len(sentence)))
    for i in siter:
        if sentence[i] == " ":
            genenrated_sentence = genenrated_sentence.append(aus.from_wav(path+"space.wav"), crossfade=250)
        elif sentence[i:i+4] in diphones:
            seg = aus.from_wav(path+sentence[i:i+4]+".wav")
            if sentence[i:i+4] in ["ގައި", "ޕޯސް"]:
                seg = speedmod(seg, 0.67, -0.4)
                seg = seg + 1.2
            genenrated_sentence = genenrated_sentence.append(seg, crossfade=180)
            next(siter, None)
            next(siter, None)
            next(siter, None)
        else:
            seg = aus.from_wav(path+sentence[i:i+2]+".wav")
            if sentence[i:i+2] in stretch:
                seg = speedmod(seg, 0.7, -0.4)
                seg = seg + 1.2
            genenrated_sentence = genenrated_sentence.append(seg, crossfade=180)
            next(siter, None)

    genenrated_sentence.export(out)

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Ensure both Phoneme directory and Output File location are defined"

    path = sys.argv[1] + "/"
    out = sys.argv[2]
    sentence = "ބޮޑު ބާޒާރުގައި ހުންނަ މޮޅު ތަކެތީގައި ސިލްޖަހަންޏާ ޕޯސްޓް އޮފީހުގެ ވެރިޔަކު ވާނީ ދާށެވެ"

    print("Generating...")
    generate_sentence(path, out, sentence)
    print("Complete!")