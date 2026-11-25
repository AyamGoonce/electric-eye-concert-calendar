(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.93cd50a8e052b8c2.js","sha256":"93cd50a8e052b8c2cc3fc4e76c017bc0ed375f6b4528fc742c07fdcdab7cb5ad","count":2092,"publishedAt":"2026-11-25T08:45:07Z","state":"calendar-state.json","stateSha256":"edcc4072b4d75c7173dfffe6ba0548ed6a199e915ee1ede37fa2c04e45d3be37","sourceState":"calendar-source-state.json","sourceStateSha256":"567a9ec54c00bd89c208a17e2a0989132f04a6a4a9cb725498d2e51ca7453275"});
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
