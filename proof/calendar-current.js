(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0f4612f1545fe606.js","sha256":"0f4612f1545fe60651e7698848080ceb33724f0754501b58474fb3497dd34733","count":2048,"publishedAt":"2026-10-30T10:11:07Z","state":"calendar-state.json","stateSha256":"0cc40960b71b59a4f3466741eead62e64f9bc98d505342d5281ba9f2fdc999ae","sourceState":"calendar-source-state.json","sourceStateSha256":"3a72fc5e055c788af89813db05edeeda3ee55c198ff433f2ec7dba5a37423322"});
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
