(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5a000a9e13c06957.js","sha256":"5a000a9e13c06957b2243fe66d726bc571a0991ef32832a2cfee8fe0a2ada104","count":2204,"publishedAt":"2026-10-03T11:15:01Z","state":"calendar-state.json","stateSha256":"249e8f05121ba7715a6be51b4ba7b3141982276fe964e1ec60e0cbc5249bcbc6","sourceState":"calendar-source-state.json","sourceStateSha256":"229bdf46fdc92d07db433744cdb04d886acf3204341d7770aad84462d256f462"});
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
