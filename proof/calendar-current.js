(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5e781e7538dbcbef.js","sha256":"5e781e7538dbcbefd0acf0398a7f88d1dc25018e3be7632cda869fc1b2a6053b","count":2049,"publishedAt":"2026-10-29T10:09:11Z","state":"calendar-state.json","stateSha256":"31a193fcf21a028eb0b7a19eae1fb7c45cb894c94888f5bf120e8421ff381767","sourceState":"calendar-source-state.json","sourceStateSha256":"e01c191a99f6dcbaf0398fb463ef436eed721937f81b233091ece7012aba8ac0"});
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
