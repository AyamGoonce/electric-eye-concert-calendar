(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.dc7b09b463367903.js","sha256":"dc7b09b4633679036e9169860ae48823b75d7063f74d417543085dd21e85972f","count":2121,"publishedAt":"2026-09-23T00:43:46Z","state":"calendar-state.json","stateSha256":"9b386cf024615a3eece9a8fa177c4b3a0aae404999be99565f9419abb9d664c3","sourceState":"calendar-source-state.json","sourceStateSha256":"d5c9804112db004392df07702ac7959fc2851b229216ab1f42b554f3cb82e4ea"});
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
