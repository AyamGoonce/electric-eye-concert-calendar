(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2fa262c044069da7.js","sha256":"2fa262c044069da7850bd3cadd79909f25dcefccbfe3217178ac34b5bc2fa0c4","count":2182,"publishedAt":"2026-10-04T12:30:29Z","state":"calendar-state.json","stateSha256":"505eddbda98350975741f8d3d3a716d1429d7f4e1a9423c6ed1174161747d320","sourceState":"calendar-source-state.json","sourceStateSha256":"d2f131ea6811112b8e876891bbbcd27e597a6390108193db9a55da829067f76f"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
