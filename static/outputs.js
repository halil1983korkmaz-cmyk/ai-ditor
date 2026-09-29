/* Save an authenticated output (PDF, Word, ZIP) from inside the signed-in page. */
window.saveOutputFile = async function (url, filename, mime, statusElement) {
  const say = text => { if (statusElement) statusElement.textContent = text; };
  try {
    if (!url || !url.startsWith('/download_file/')) throw new Error('Önce çıktıyı oluşturun.');
    say('Dosya alınıyor…');
    const response = await aiditorFetch(url, {credentials: 'same-origin'});
    if (!response.ok) {
      const result = await response.json().catch(() => ({}));
      throw new Error(result.error || 'Dosya indirilemedi. Çıktıyı yeniden oluşturun.');
    }
    const blob = await response.blob();
    const head = new Uint8Array(await blob.slice(0, 4).arrayBuffer());
    const isPdf = head.join(',') === '37,80,68,70', isZip = head.join(',') === '80,75,3,4';
    if (blob.size < 22 || !(mime === 'application/pdf' ? isPdf : isZip)) throw new Error('Dosya eksik veya geçersiz. Çıktıyı yeniden oluşturun.');
    if (window.pywebview) {
      if (typeof window.pywebview.api?.save_output !== 'function') throw new Error('Kaydetme bağlantısı hazır değil. Uygulamayı yeniden açın.');
      const encoded = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = () => reject(new Error('Dosya okunamadı.'));
        reader.readAsDataURL(blob);
      });
      const result = await window.pywebview.api.save_output(filename, encoded);
      if (!result?.ok) throw new Error(result?.error || 'Dosya kaydedilemedi.');
      say(result.cancelled ? 'Kaydetme iptal edildi. Yeniden deneyebilirsiniz.' : 'Dosya kaydedildi.');
    } else {
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl; link.download = filename;
      document.body.append(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(objectUrl), 60000);
      say('Dosya tarayıcının indirme listesine gönderildi.');
    }
  } catch (error) {
    say('Hata: ' + error.message);
  }
};
