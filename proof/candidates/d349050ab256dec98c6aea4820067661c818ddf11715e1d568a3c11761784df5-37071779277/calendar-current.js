(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d349050ab256dec9.js","sha256":"d349050ab256dec98c6aea4820067661c818ddf11715e1d568a3c11761784df5","count":2219,"publishedAt":"2026-10-02T22:19:08Z","state":"calendar-state.json","stateSha256":"5ce6ed8bd02144c0816cc75ce49653489a1115585fe1cb53fd6545826ad9d93e","sourceState":"calendar-source-state.json","sourceStateSha256":"daa331faa451e6f9d5b737e48c8ba146d495b9430363895c96c94e52491376f6"});
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
