(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e509824dcb3de4a8.js","sha256":"e509824dcb3de4a8adfb2cf5fe41bf794969bd615ed5393f37afa9ce299ee91b","count":2221,"publishedAt":"2026-10-01T06:35:26Z","state":"calendar-state.json","stateSha256":"9f57ebb961cf495588ffdad4f64dc6c7f8592c366515a8fa09eb260d92709df5","sourceState":"calendar-source-state.json","sourceStateSha256":"fdb3fbe07d6df5864aaab6449b0e6206e35b08848054c9150335df270b33125d"});
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
