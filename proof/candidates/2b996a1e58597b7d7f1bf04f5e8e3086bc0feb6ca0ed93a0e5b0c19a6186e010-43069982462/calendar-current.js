(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2b996a1e58597b7d.js","sha256":"2b996a1e58597b7d7f1bf04f5e8e3086bc0feb6ca0ed93a0e5b0c19a6186e010","count":2164,"publishedAt":"2026-11-11T17:39:28Z","state":"calendar-state.json","stateSha256":"be8fbdb7802527600e38b864c80825c4b000248dc34dedda564c0578c4e53eb0","sourceState":"calendar-source-state.json","sourceStateSha256":"03acde7eaf5e1052607814e826f52953a6b92c70099bc4b83f37b5789e689f3d"});
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
